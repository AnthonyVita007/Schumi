
import React from 'react';
import { Link } from 'react-router-dom';

const StepCard: React.FC<{ number: string; title: string; description: string }> = ({ number, title, description }) => (
  <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-brand-primary">
    <div className="flex items-center mb-4">
      <span className="flex items-center justify-center w-10 h-10 rounded-full bg-brand-primary text-white font-bold text-xl mr-4">{number}</span>
      <h3 className="text-xl font-semibold text-brand-text-dark">{title}</h3>
    </div>
    <p className="text-brand-text-light">{description}</p>
  </div>
);

const LandingPage: React.FC = () => {
  return (
    <div className="container mx-auto">
      <div className="text-center py-12 px-4">
        <h1 className="text-4xl md:text-5xl font-extrabold text-brand-text-dark mb-4">Sistema di Gestione e Valutazione Autisti</h1>
        <p className="text-lg md:text-xl text-brand-text-light max-w-3xl mx-auto">
          Una piattaforma integrata per registrare, analizzare e monitorare le performance dei tuoi autisti, migliorando sicurezza ed efficienza.
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
        <StepCard 
          number="1"
          title="Simulazione"
          description="L'autista completa una sessione di guida simulata. I dati vengono raccolti in un file CSV per l'analisi."
        />
        <StepCard 
          number="2"
          title="Registrazione"
          description="Registra un nuovo autista nel sistema, allegando il file CSV della sua simulazione."
        />
        <StepCard 
          number="3"
          title="Classificazione"
          description="Il nostro sistema analizza i dati di simulazione per classificare lo stile di guida dell'autista."
        />
        <StepCard 
          number="4"
          title="Monitoraggio"
          description="Monitora lo stato emotivo e il comportamento dell'autista in tempo reale durante la guida."
        />
      </div>

      <div className="text-center">
        <Link 
          to="/drivers" 
          className="inline-block bg-brand-primary text-white font-bold py-3 px-8 rounded-full text-lg hover:bg-green-600 transition-transform transform hover:scale-105 shadow-lg">
          Inizia a Gestire gli Autisti
        </Link>
      </div>
    </div>
  );
};

export default LandingPage;
