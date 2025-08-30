
import React from 'react';

export const MonitorIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
    <svg 
        xmlns="http://www.w3.org/2000/svg" 
        fill="none" 
        viewBox="0 0 24 24" 
        strokeWidth={1.5} 
        stroke="currentColor" 
        {...props}
    >
        <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-1.621-.87a3 3 0 01-.879-2.122v-1.007M15 9.75a3 3 0 11-6 0 3 3 0 016 0z" 
        />
        <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            d="M12 15.75a4.5 4.5 0 004.5-4.5V8.25a4.5 4.5 0 00-4.5-4.5A4.5 4.5 0 007.5 8.25v3a4.5 4.5 0 004.5 4.5z" 
        />
    </svg>
);
