
import React, { useRef, useEffect, useState } from 'react';

const WebcamFeed: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    let stream: MediaStream | null = null;
    
    const getCamera = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        setStatus('success');
      } catch (err) {
        setStatus('error');
        if (err instanceof Error) {
            if (err.name === 'NotAllowedError') {
                setErrorMsg('Accesso alla webcam negato. Controlla le autorizzazioni del browser.');
            } else {
                setErrorMsg('Impossibile accedere alla webcam.');
            }
        } else {
            setErrorMsg('Errore sconosciuto.');
        }
      }
    };

    getCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="aspect-w-4 aspect-h-3 bg-black rounded-md overflow-hidden relative">
      <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover" />
      {status === 'loading' && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-75">
          <p className="text-white">Inizializzazione webcam...</p>
        </div>
      )}
      {status === 'error' && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-900 bg-opacity-75 p-4">
          <p className="text-white text-center text-sm">{errorMsg}</p>
        </div>
      )}
    </div>
  );
};

export default WebcamFeed;
