
import { Driver, Classification, MonitoringStatus } from '../types';

let drivers: Driver[] = [
  {
    id: 1,
    firstName: 'Mario',
    lastName: 'Rossi',
    classification: Classification.EFFICIENT,
    monitoringStatus: MonitoringStatus.OFFLINE,
    simulationFile: 'sim_mario_rossi.csv',
  },
  {
    id: 2,
    firstName: 'Giulia',
    lastName: 'Bianchi',
    classification: Classification.UNCLASSIFIED,
    monitoringStatus: MonitoringStatus.ONLINE,
    simulationFile: 'sim_giulia_bianchi.csv'
  },
  {
    id: 3,
    firstName: 'Luca',
    lastName: 'Verdi',
    classification: Classification.BEGINNER,
    monitoringStatus: MonitoringStatus.OFFLINE,
    simulationFile: 'sim_luca_verdi.csv'
  },
];

let nextId = 4;

const simulateDelay = <T,>(data: T): Promise<T> => {
  return new Promise(resolve => setTimeout(() => resolve(data), 500 + Math.random() * 500));
};

export const getDrivers = async (): Promise<Driver[]> => {
  return simulateDelay([...drivers]);
};

export const getDriverById = async (id: number): Promise<Driver | undefined> => {
  const driver = drivers.find(d => d.id === id);
  return simulateDelay(driver ? { ...driver } : undefined);
};

export const addDriver = async (
  firstName: string,
  lastName: string,
  file: File
): Promise<Driver> => {
  const newDriver: Driver = {
    id: nextId++,
    firstName,
    lastName,
    classification: Classification.UNCLASSIFIED,
    monitoringStatus: MonitoringStatus.OFFLINE,
    simulationFile: file.name,
  };
  drivers.push(newDriver);
  return simulateDelay(newDriver);
};

export const classifyDriver = async (id: number): Promise<Classification> => {
  const classifications = [Classification.BEGINNER, Classification.EFFICIENT, Classification.EXPERT];
  const randomClassification = classifications[Math.floor(Math.random() * classifications.length)];
  
  const driverIndex = drivers.findIndex(d => d.id === id);
  if (driverIndex !== -1) {
    drivers[driverIndex].classification = randomClassification;
  }
  
  // Simulate a longer delay for classification
  return new Promise(resolve => setTimeout(() => resolve(randomClassification), 1500 + Math.random() * 1000));
};
