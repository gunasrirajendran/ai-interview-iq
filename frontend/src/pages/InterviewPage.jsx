import { useEffect, useMemo, useRef, useState } from 'react';
import api from '../lib/api';

const interviewTypes = ['HR', 'Java', 'Python', 'SQL', 'DSA', 'Custom Interview'];
const difficulties = ['Easy', 'Medium', 'Hard'];
const companyModes = ['Google', 'Microsoft', 'Amazon', 'Zoho', 'TCS', 'Infosys'];

export default function InterviewPage() {
  const [selectedType, setSelectedType] = useState('Python');
  const [selectedDifficulty, setSelectedDifficulty] = useState('Medium');
  const [selectedCompany, setSelectedCompany] = useState('');
  const [companyMeta, setCompanyMeta] = useState(null);
  const [question, setQuestion] = useState('Select a role and start the interview to generate your questions.');
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [transcript, setTranscript] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [started, setStarted] = useState(false);
  const [timer, setTimer] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const [interviewId, setInterviewId] = useState(null);
  const [questionId, setQuestionId] = useState(null);
  const [cameraStatus, setCameraStatus] = useState('stopped');
  const [cameraError, setCameraError] = useState('');
  const [analytics, setAnalytics] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const frameTimerRef = useRef(null);
  const cameraStatusRef = useRef(cameraStatus);

  useEffect(() => {
    if (!started) return;
    const interval = window.setInterval(() => setTimer((prev) => prev + 1), 1000);
    return () => window.clearInterval(interval);
  }, [started]);

  useEffect(() => {
    cameraStatusRef.current = cameraStatus;
  }, [cameraStatus]);

  useEffect(() => {
    return () => {
      if (frameTimerRef.current) window.clearInterval(frameTimerRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    api.get('/company-modes/companies').then((res) => {
      if (res.data?.length) setCompanyMeta(res.data[0]);
    }).catch(() => {});
  }, []);

  const currentQuestion = useMemo(() => questions[currentIndex] || null, [questions, currentIndex]);
  const speakingSpeed = useMemo(() => {
    const words = transcript.split(/\s+/).filter(Boolean).length;
    return timer > 0 ? Math.round((words / Math.max(timer, 1)) * 60) : 0;
  }, [transcript, timer]);
  const fillerWordCount = useMemo(() => {
    const fillers = ['um', 'uh', 'like', 'actually', 'basically', 'so', 'you know'];
    const text = `${answer} ${transcript}`.toLowerCase();
    return fillers.reduce((count, filler) => count + (text.split(filler).length - 1), 0);
  }, [answer, transcript]);

  const startWebcam = async () => {
    if (typeof navigator === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
      setCameraStatus('error');
      setCameraError('Webcam API is not available in this browser.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch(() => {});
      }
      cameraStatusRef.current = 'live';
      setCameraStatus('live');
      setCameraError('');
      if (frameTimerRef.current) window.clearInterval(frameTimerRef.current);
      frameTimerRef.current = window.setInterval(() => {
        if (!videoRef.current || !canvasRef.current || !interviewId || cameraStatusRef.current !== 'live') return;
        const video = videoRef.current;
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');
        if (!context || video.readyState < 2) {
          setCameraStatus('disconnected');
          setCameraError('Camera disconnected.');
          return;
        }
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg', 0.75);
        api.post(`/analytics/live/${interviewId}`, { image: imageData }).then((response) => {
          setAnalytics(response.data);
          setWarnings(response.data.warnings || []);
          if (response.data.camera_disconnected) {
            setCameraStatus('disconnected');
            setCameraError('Camera disconnected.');
          } else {
            setCameraStatus('live');
          }
        }).catch(() => {
          setCameraStatus('disconnected');
          setCameraError('Unable to stream analytics.');
        });
      }, 1000);
    } catch (err) {
      cameraStatusRef.current = 'error';
      setCameraStatus('error');
      setCameraError('Camera permission was denied or the device is unavailable.');
    }
  };

  const stopWebcam = () => {
    if (frameTimerRef.current) {
      window.clearInterval(frameTimerRef.current);
      frameTimerRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    cameraStatusRef.current = 'stopped';
    setCameraStatus('stopped');
    setCameraError('');
  };

  const startInterview = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.post('/interview/start', {
        role: selectedCompany ? selectedCompany.toLowerCase() : selectedType.toLowerCase(),
        difficulty: selectedDifficulty.toLowerCase(),
        duration_minutes: 5,
      });
      setQuestions(response.data.questions.map((q, idx) => ({ id: idx + 1, text: q })));
      setCurrentIndex(0);
      setInterviewId(response.data.interview_id);
      setQuestionId(response.data.first_question_id);
      setQuestion(response.data.first_question);
      setStarted(true);
      setTimer(0);
      setFeedback(null);
      setAnswer('');
      setTranscript('');
      if (cameraStatus !== 'live') {
        await startWebcam();
      }
    } catch (err) {
      setError('Unable to start the interview. Please ensure the backend is running and the Gemini API key is configured.');
    } finally {
      setLoading(false);
    }
  };

  const handleNextQuestion = async () => {
    if (!answer.trim()) {
      setError('Please provide an answer before moving on.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const response = await api.post('/interview/answer', {
        interview_id: interviewId,
        question_id: questionId,
        answer,
        transcript,
      });
      setFeedback(response.data.evaluation);
      if (response.data.next_question) {
        setQuestions((prev) => [...prev, { id: response.data.next_question.id, text: response.data.next_question.text }]);
        setQuestion(response.data.next_question.text);
        setQuestionId(response.data.next_question.id);
        setCurrentIndex((prev) => prev + 1);
      } else {
        await api.post(`/interview/end?interview_id=${interviewId}`);
        setQuestion('Interview completed. Review your report and continue practicing.');
        stopWebcam();
      }
      setAnswer('');
      setTranscript('');
    } catch (err) {
      setError('The answer could not be evaluated. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];
      recorder.ondataavailable = (event) => chunksRef.current.push(event.data);
      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('file', blob, 'answer.webm');
        try {
          const response = await api.post('/interview/audio', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });
          setTranscript(response.data.transcript || '');
        } catch (err) {
          setError('Audio upload failed.');
        }
      };
      recorder.start();
      setError('');
    } catch (err) {
      setError('Microphone access was denied or unavailable.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Live Interview Session</h2>
          <div className="rounded-full bg-cyan-500/20 px-3 py-1 text-sm text-cyan-300">{timer}s</div>
        </div>
        <div className="mt-6 rounded-2xl border border-slate-700 bg-slate-800/80 p-4">
          <p className="text-sm text-slate-400">Current Question</p>
          <p className="mt-2 text-lg">{currentQuestion?.text || question}</p>
        </div>
        <div className="mt-4 overflow-hidden rounded-2xl border border-slate-700 bg-black">
          <video ref={videoRef} className="h-72 w-full object-cover" playsInline muted />
          <canvas ref={canvasRef} className="hidden" />
          <div className="absolute left-3 top-3 rounded-full bg-slate-950/70 px-3 py-1 text-xs text-slate-200">
            Camera: {cameraStatus}
          </div>
          <div className="absolute bottom-3 right-3 max-w-xs rounded-xl border border-slate-700 bg-slate-900/80 p-3 text-xs text-slate-300">
            <div className="font-medium text-cyan-300">Live analytics</div>
            <div>Eye Contact: {analytics?.eye_contact_percentage ?? 0}%</div>
            <div>Head Position: {analytics?.head_pose ?? 'Straight'}</div>
            <div>Face Detected: {analytics?.face_detected ? 'Yes' : 'No'}</div>
            <div>Speaking Speed: {speakingSpeed} wpm</div>
            <div>Filler Words: {fillerWordCount}</div>
          </div>
        </div>
        <div className="mt-4 flex gap-3">
          <button onClick={startWebcam} className="rounded-xl bg-cyan-600 px-4 py-2 text-sm font-medium">Start Webcam</button>
          <button onClick={stopWebcam} className="rounded-xl bg-slate-700 px-4 py-2 text-sm font-medium">Stop Webcam</button>
        </div>
        {cameraError ? <div className="mt-3 rounded-lg border border-rose-500/40 bg-rose-500/10 p-2 text-sm text-rose-300">{cameraError}</div> : null}
        {warnings.length > 0 ? (
          <div className="mt-3 rounded-lg border border-amber-500/40 bg-amber-500/10 p-2 text-sm text-amber-300">{warnings.join(' • ')}</div>
        ) : null}
        <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} className="mt-4 min-h-36 w-full rounded-xl border border-slate-700 bg-slate-800 p-4" placeholder="Type your answer here..." />
        <div className="mt-4 text-sm text-slate-400">Transcript: {transcript || 'No transcript yet.'}</div>
        <div className="mt-6 grid gap-3 md:grid-cols-3">
          <button onClick={startInterview} className="rounded-xl bg-cyan-600 px-4 py-3 font-medium" disabled={loading}>{loading ? 'Starting...' : 'Start Interview'}</button>
          <button onClick={startRecording} className="rounded-xl bg-slate-700 px-4 py-3 font-medium">Record Audio</button>
          <button onClick={stopRecording} className="rounded-xl bg-emerald-600 px-4 py-3 font-medium">Stop Recording</button>
        </div>
        <div className="mt-4 flex gap-3">
          <button onClick={handleNextQuestion} className="rounded-xl bg-violet-600 px-4 py-3 font-medium" disabled={loading || !started}>Next Question</button>
          <button onClick={() => { setStarted(false); stopWebcam(); }} className="rounded-xl bg-rose-600 px-4 py-3 font-medium">End Interview</button>
        </div>
        {error ? <div className="mt-4 rounded-lg border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-300">{error}</div> : null}
      </div>

      <div className="space-y-6">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
          <h3 className="text-lg font-semibold">Interview Type</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {interviewTypes.map((type) => (
              <button key={type} onClick={() => setSelectedType(type)} className={`rounded-full px-3 py-2 text-sm ${selectedType === type ? 'bg-cyan-600' : 'bg-slate-800'}`}>
                {type}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
          <h3 className="text-lg font-semibold">Company Mode</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {companyModes.map((company) => (
              <button key={company} onClick={() => setSelectedCompany(company)} className={`rounded-full px-3 py-2 text-sm ${selectedCompany === company ? 'bg-cyan-600' : 'bg-slate-800'}`}>
                {company}
              </button>
            ))}
          </div>
          {companyMeta ? <p className="mt-3 text-sm text-slate-400">Focus: {companyMeta.focus}</p> : null}
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
          <h3 className="text-lg font-semibold">Difficulty</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {difficulties.map((level) => (
              <button key={level} onClick={() => setSelectedDifficulty(level)} className={`rounded-full px-3 py-2 text-sm ${selectedDifficulty === level ? 'bg-cyan-600' : 'bg-slate-800'}`}>
                {level}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
          <h3 className="text-lg font-semibold">AI Feedback Snapshot</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-300">
            <li>• Technical: {feedback?.technical_score ?? '—'}</li>
            <li>• Communication: {feedback?.communication_score ?? '—'}</li>
            <li>• Relevance: {feedback?.relevance_score ?? '—'}</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
