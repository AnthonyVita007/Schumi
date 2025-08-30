
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { EmotionDataPoint } from '../types';

interface EmotionChartProps {
  data: EmotionDataPoint[];
}

const EmotionChart: React.FC<EmotionChartProps> = ({ data }) => {
  return (
    <div className="w-full h-80">
        <ResponsiveContainer>
        <LineChart
            data={data}
            margin={{
            top: 5,
            right: 20,
            left: -10,
            bottom: 5,
            }}
        >
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="time" stroke="#555" />
            <YAxis stroke="#555" domain={[0, 100]}/>
            <Tooltip
                contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                    border: '1px solid #ccc',
                    borderRadius: '5px',
                }}
            />
            <Legend />
            <Line type="monotone" dataKey="stress" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="Stress" />
            <Line type="monotone" dataKey="focus" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="Focus" />
            <Line type="monotone" dataKey="calm" stroke="#22c55e" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="Calma" />
        </LineChart>
        </ResponsiveContainer>
    </div>
  );
};

export default EmotionChart;
