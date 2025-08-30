import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Driver, EmotionDataPoint } from '../types';
import { getDriverById } from '../services/driverService';
import WebcamFeed from '../components/WebcamFeed';
import EmotionChart from '../components/EmotionChart';
import Spinner from '../components/Spinner';

const generateInitialData = (): EmotionDataPoint[] => {
  const data: EmotionDataPoint[] = [];
  for (let i = 5; i >= 0; i--) {
    const time = new Date(Date.now() - i * 3000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit'});
    data.push({
      time,
      stress: Math.floor(Math.random() * 20) + 10,
      focus: Math.floor(Math.random() * 30) + 60,
      calm: Math.floor(Math.random() * 20) + 40,
    });
  }
  return data;
};

const MonitorPage: React.FC = () => {
  const { driverId } = useParams<{ driverId: string }>();
  const [driver, setDriver] = useState<Driver | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [emotionData, setEmotionData] = useState<EmotionDataPoint[]>(generateInitialData());

  const fetchDriver = useCallback(async () => {
    if (driverId) {
      setIsLoading(true);
      const fetchedDriver = await getDriverById(parseInt(driverId, 10));
      setDriver(fetchedDriver || null);
      setIsLoading(false);
    }
  }, [driverId]);

  useEffect(() => {
    fetchDriver();
  }, [fetchDriver]);

  useEffect(() => {
    const interval = setInterval(() => {
      setEmotionData(prevData => {
        const newData = [...prevData.slice(1)];
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit'});
        const lastDataPoint = newData[newData.length - 1];
        newData.push({
          time,
          // FIX: Replaced .at(-1) with array[array.length - 1] to support older JavaScript versions.
          stress: Math.max(10, Math.min(90, (lastDataPoint?.stress ?? 30) + (Math.random() - 0.5) * 10)),
          // FIX: Replaced .at(-1) with array[array.length - 1] to support older JavaScript versions.
          focus: Math.max(10, Math.min(90, (lastDataPoint?.focus ?? 70) + (Math.random() - 0.5) * 10)),
          // FIX: Replaced .at(-1) with array[array.length - 1] to support older JavaScript versions.
          calm: Math.max(10, Math.min(90, (lastDataPoint?.calm ?? 50) + (Math.random() - 0.5) * 10)),
        });
        return newData;
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner />
      </div>
    );
  }

  if (!driver) {
    return (
      <div className="text-center">
        <h2 className="text-2xl font-bold">Autista non trovato</h2>
      </div>
    );
  }

  return (
    <div className="container mx-auto">
      <h1 className="text-3xl font-bold text-brand-text-dark mb-2">
        Monitoraggio: <span className="text-brand-primary">{driver.firstName} {driver.lastName}</span>
      </h1>
      <p className="text-brand-text-light mb-6">Sessione di monitoraggio in tempo reale.</p>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 bg-white p-4 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-brand-text-dark">Webcam Feed</h2>
          <WebcamFeed />
        </div>
        <div className="lg:col-span-2 bg-white p-4 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-brand-text-dark">Analisi Emotiva</h2>
          <EmotionChart data={emotionData} />
        </div>
      </div>
    </div>
  );
};

export default MonitorPage;