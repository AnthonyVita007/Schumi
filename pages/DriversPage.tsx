
import React, { useState, useEffect, useCallback } from 'react';
import { Driver } from '../types';
import { getDrivers, addDriver, classifyDriver } from '../services/driverService';
import DriverCard from '../components/DriverCard';
import AddDriverModal from '../components/AddDriverModal';
import Spinner from '../components/Spinner';
import { PlusIcon } from '../components/icons/PlusIcon';

const DriversPage: React.FC = () => {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchDrivers = useCallback(async () => {
    setIsLoading(true);
    const fetchedDrivers = await getDrivers();
    setDrivers(fetchedDrivers);
    setIsLoading(false);
  }, []);

  useEffect(() => {
    fetchDrivers();
  }, [fetchDrivers]);

  const handleAddDriver = async (firstName: string, lastName: string, file: File) => {
    const newDriver = await addDriver(firstName, lastName, file);
    setDrivers(prevDrivers => [...prevDrivers, newDriver]);
    setIsModalOpen(false);
  };

  const handleClassify = async (id: number) => {
    const newClassification = await classifyDriver(id);
    setDrivers(prevDrivers =>
      prevDrivers.map(d => (d.id === id ? { ...d, classification: newClassification } : d))
    );
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="container mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-brand-text-dark">Elenco Autisti</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center bg-brand-primary text-white font-bold py-2 px-4 rounded-lg hover:bg-green-600 transition-colors shadow"
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Aggiungi Autista
        </button>
      </div>

      {drivers.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {drivers.map(driver => (
            <DriverCard key={driver.id} driver={driver} onClassify={handleClassify} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-white rounded-lg shadow">
            <p className="text-brand-text-light">Nessun autista trovato. Aggiungine uno per iniziare.</p>
        </div>
      )}

      <AddDriverModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAddDriver={handleAddDriver}
      />
    </div>
  );
};

export default DriversPage;
