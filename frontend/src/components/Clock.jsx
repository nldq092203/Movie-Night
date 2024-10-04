import React, { useEffect, useState } from 'react';
import { differenceInSeconds } from 'date-fns';

function Clock({ startTime }) {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [timeLeft, setTimeLeft] = useState('');

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentTime(new Date());

      // Calculate time left
      if (startTime) {
        const now = new Date();
        const startDate = new Date(startTime);
        const secondsLeft = differenceInSeconds(startDate, now);

        if (secondsLeft > 0) {
          const hours = Math.floor(secondsLeft / 3600);
          const minutes = Math.floor((secondsLeft % 3600) / 60);
          const seconds = secondsLeft % 60;
          setTimeLeft(`${hours}h ${minutes}m ${seconds}s`);
        } else {
          setTimeLeft('The event has started!');
        }
      }
    }, 1000);

    return () => clearInterval(intervalId);
  }, [startTime]);

  // Function to format the time in HH:MM:SS
  const formatTime = (date) => {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
  };

  // Function to format the date
  const formatDate = (date) => {
    const options = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    };
    return date.toLocaleDateString(undefined, options);
  };

  return (
    <div className="flex flex-col items-center text-white">
      {/* Current Time */}
      <div className="flex space-x-2 text-6xl font-bold mb-4">
        {formatTime(currentTime).split(':').map((num, index) => (
          <div key={index} className="bg-gray-800 p-4 rounded-md shadow-lg">
            {num}
          </div>
        ))}
      </div>
      <div className="text-xl font-light">{formatDate(currentTime)}</div>

      {/* Countdown (if startTime is provided) */}
      {startTime && (
        <div className="mt-4 text-2xl">
          <strong>Countdown:</strong> {timeLeft}
        </div>
      )}
    </div>
  );
}

export default Clock;