
export enum Classification {
  UNCLASSIFIED = "Non Classificato",
  BEGINNER = "Principiante",
  EFFICIENT = "Efficiente",
  EXPERT = "Esperto",
}

export enum MonitoringStatus {
  OFFLINE = "Offline",
  ONLINE = "Online",
  MONITORING = "In Corso",
}

export interface Driver {
  id: number;
  firstName: string;
  lastName: string;
  classification: Classification;
  monitoringStatus: MonitoringStatus;
  simulationFile?: string;
}

export interface EmotionDataPoint {
  time: string;
  stress: number;
  focus: number;
  calm: number;
}
