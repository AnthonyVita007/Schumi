
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Driver, Classification, MonitoringStatus } from '../types';
import { MonitorIcon } from './icons/MonitorIcon';
import { BrainIcon } from './icons/BrainIcon';

interface DriverCardProps {
  driver: Driver;
  onClassify: (id: number) => void;
}

const DriverCard: React.FC<DriverCardProps> = ({ driver, onClassify }) => {
  const [isClassifying, setIsClassifying] = useState(false);

  const handleClassifyClick = async () => {
    setIsClassifying(true);
    await onClassify(driver.id);
    setIsClassifying(false);
  };

  const getStatusColor = (status: MonitoringStatus) => {
    switch (status) {
      case MonitoringStatus.ONLINE:
        return 'bg-green-500';
      case MonitoringStatus.MONITORING:
        return 'bg-blue-500';
      case MonitoringStatus.OFFLINE:
        return 'bg-gray-400';
      default:
        return 'bg-gray-400';
    }
  };

  const getClassificationStyle = (classification: Classification) => {
    switch (classification) {
        case Classification.EXPERT:
            return 'text-green-600 bg-green-100';
        case Classification.EFFICIENT:
            return 'text-blue-600 bg-blue-100';
        case Classification.BEGINNER:
            return 'text-yellow-600 bg-yellow-100';
        default:
            return 'text-gray-600 bg-gray-100';
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden transform hover:-translate-y-1 transition-transform duration-300 flex flex-col">
      <div className="p-5 flex-grow">
        <div className="flex justify-between items-start">
            <h3 className="text-xl font-bold text-brand-text-dark">{driver.firstName} {driver.lastName}</h3>
            <div className="flex items-center">
                <span className={`w-3 h-3 rounded-full mr-2 ${getStatusColor(driver.monitoringStatus)}`}></span>
                <span className="text-xs font-medium text-brand-text-light">{driver.monitoringStatus}</span>
            </div>
        </div>
        <p className="text-sm text-gray-500 mb-4">ID: DRV-{String(driver.id).padStart(4, '0')}</p>

        <div className={`inline-block px-3 py-1 text-sm font-semibold rounded-full ${getClassificationStyle(driver.classification)}`}>
            {driver.classification}
        </div>
      </div>
      <div className="bg-gray-50 p-4 flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
        <button
          onClick={handleClassifyClick}
          disabled={isClassifying || driver.classification !== Classification.UNCLASSIFIED}
          className="flex-1 flex items-center justify-center text-sm bg-brand-secondary text-brand-text-dark font-semibold py-2 px-4 rounded-md hover:bg-green-300 transition-colors disabled:bg-gray-200 disabled:cursor-not-allowed disabled:text-gray-500"
        >
          <BrainIcon className="w-4 h-4 mr-2"/>
          {isClassifying ? 'Classificazione...' : 'Classifica'}
        </button>
        <Link
          to={`/monitor/${driver.id}`}
          className="flex-1 flex items-center justify-center text-sm bg-brand-primary text-white font-semibold py-2 px-4 rounded-md hover:bg-green-600 transition-colors"
        >
          <MonitorIcon className="w-4 h-4 mr-2"/>
          Monitora
        </Link>
      </div>
    </div>
  );
};

export default DriverCard;
