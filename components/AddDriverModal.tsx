
import React, { useState, FormEvent } from 'react';

interface AddDriverModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddDriver: (firstName: string, lastName: string, file: File) => Promise<void>;
}

const AddDriverModal: React.FC<AddDriverModalProps> = ({ isOpen, onClose, onAddDriver }) => {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!firstName || !lastName || !file) {
      setError('Tutti i campi sono obbligatori.');
      return;
    }
    setError('');
    setIsSubmitting(true);
    await onAddDriver(firstName, lastName, file);
    setIsSubmitting(false);
    // Reset form
    setFirstName('');
    setLastName('');
    setFile(null);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div className="p-6 border-b">
          <h2 className="text-2xl font-bold text-brand-text-dark">Aggiungi Nuovo Autista</h2>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="p-6 space-y-4">
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <div>
              <label htmlFor="firstName" className="block text-sm font-medium text-brand-text-light">Nome</label>
              <input
                type="text"
                id="firstName"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-brand-primary focus:border-brand-primary"
                required
              />
            </div>
            <div>
              <label htmlFor="lastName" className="block text-sm font-medium text-brand-text-light">Cognome</label>
              <input
                type="text"
                id="lastName"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-brand-primary focus:border-brand-primary"
                required
              />
            </div>
            <div>
              <label htmlFor="file" className="block text-sm font-medium text-brand-text-light">File Simulazione (CSV)</label>
              <input
                type="file"
                id="file"
                accept=".csv"
                onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-brand-secondary file:text-brand-text-dark hover:file:bg-green-200"
                required
              />
              {file && <p className="text-xs text-gray-500 mt-1">{file.name}</p>}
            </div>
          </div>
          <div className="bg-gray-50 p-4 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Annulla
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-brand-primary border border-transparent rounded-md shadow-sm hover:bg-green-600 disabled:bg-gray-400"
            >
              {isSubmitting ? 'Aggiungendo...' : 'Aggiungi Autista'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddDriverModal;
