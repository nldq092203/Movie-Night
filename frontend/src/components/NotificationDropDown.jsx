import React, { useState, useEffect } from 'react';
import { BellIcon } from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import { useMovieNightContext } from '../context/MovieNightContext';

function NotificationDropdown() {
  const [open, setOpen] = useState(false);
  const { saveInvitationData } = useMovieNightContext(); 
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState('ALL'); 
  const [isReadFilter, setIsReadFilter] = useState('ALL'); 
  const navigate = useNavigate();

  const POLLING_INTERVAL = 30000;

  const fetchNotifications = async () => {
    try {
      const accessToken = localStorage.getItem('access_token');

      let filterParams = '';
      if (isReadFilter !== 'ALL') {
        filterParams += `&is_read=${isReadFilter === 'READ'}`;
      }
      if (filterType !== 'ALL') {
        filterParams += `&notification_type=${filterType}`;
      }

      const response = await fetch(`http://0.0.0.0:8000/api/v1/notifications/?ordering=-timestamp${filterParams}`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      setNotifications(data.results || []);
      setUnreadCount(data.unreadCount || 0);
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
      setError('Failed to fetch notifications.');
    }
  };

  useEffect(() => {
    fetchNotifications();

    const interval = setInterval(() => {
      fetchNotifications();
    }, POLLING_INTERVAL);

    return () => clearInterval(interval);
  }, [filterType, isReadFilter]);

  const toggleDropdown = () => {
    setOpen(!open);
  };

  // Function to mark a notification as read
  const markAsRead = async (notificationId) => {
    const accessToken = localStorage.getItem('access_token');
    try {
      const response = await fetch(`http://0.0.0.0:8000/api/v1/notifications/${notificationId}/mark-read/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to mark notification as read');
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleNotificationClick = (notification) => {
    const { id, notification_type, object_id, content_object } = notification;

    // Mark notification as read
    if(!notification.is_read){
      markAsRead(id);
    }

    // Handle navigation and actions based on notification type
    if (['REM', 'UPD'].includes(notification_type)) {
      navigate(`/movie-nights/${object_id}`);
    } else if (notification_type === 'CAN') {
      alert('This notification is a cancellation.');
    } else if (notification_type === 'RES') {
      navigate(`/movie-nights/${content_object.movie_night_id}`);
    } else if (notification_type === 'INV') {
      saveInvitationData({
        attendanceConfirmed: content_object.attendance_confirmed,
        isAttending: content_object.is_attending,
        movienight_invitation_id: object_id,
      });
      navigate(`/movie-nights/${content_object.movie_night_id}`);
    }
  };

  const isToday = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    );
  };

  return (
    <div className="fixed bottom-5 right-5 z-50">
      <div className="relative">
        <button
          onClick={toggleDropdown}
          className="bg-blue-600 text-white rounded-full p-3 shadow-lg hover:bg-blue-700 focus:outline-none"
        >
          <BellIcon className="h-6 w-6" />
          {unreadCount > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-600 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
              {unreadCount}
            </span>
          )}
        </button>

        {open && (
          <div className="absolute right-0 bottom-full mb-4 w-96 bg-black text-white rounded-lg shadow-xl ring-1 ring-black ring-opacity-5 max-h-96 overflow-y-auto transition-transform transform">
            <div className="py-2">
              <h2 className="text-xl font-bold px-4 mb-2">Notifications</h2>

              <div className="px-4 flex space-x-2 mb-2">
                <select
                  className="bg-gray-800 text-white px-2 py-1 rounded"
                  value={isReadFilter}
                  onChange={(e) => setIsReadFilter(e.target.value)}
                >
                  <option value="ALL">All</option>
                  <option value="READ">Read</option>
                  <option value="UNREAD">Unread</option>
                </select>
                <select
                  className="bg-gray-800 text-white px-2 py-1 rounded"
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                >
                  <option value="ALL">All Types</option>
                  <option value="INV">Invites</option>
                  <option value="UPD">Updates</option>
                  <option value="REM">Reminders</option>
                  <option value="CAN">Cancels</option>
                  <option value="RES">Responses</option>
                </select>
              </div>

              <div className="divide-y divide-gray-600">
                <div className="px-4 py-2">
                  <h3 className="text-lg font-semibold mb-2">This day</h3>
                  {notifications.filter(notification => isToday(notification.timestamp)).length === 0 ? (
                    <p className="text-gray-600">No notifications today</p>
                  ) : (
                    notifications
                      .filter(notification => isToday(notification.timestamp))
                      .map((notification) => (
                        <div
                          key={notification.id}
                          className={`py-2 flex justify-between items-center ${
                            !notification.is_read ? 'bg-gray-800' : 'bg-gray-900'
                          } cursor-pointer`}
                          onClick={() => handleNotificationClick(notification)}
                        >
                          <div className="flex items-center">
                            <img
                              src="https://via.placeholder.com/40"
                              alt="User"
                              className="rounded-full h-8 w-8 mr-2"
                            />
                            <div>
                              <p className="font-semibold text-sm">{notification.message}</p>
                              <p className="text-xs text-gray-400">{new Date(notification.timestamp).toLocaleString()}</p>
                            </div>
                          </div>
                        </div>
                      ))
                  )}
                </div>

                <div className="px-4 py-2">
                  <h3 className="text-lg font-semibold mb-2">This week</h3>
                  {notifications.filter(notification => !isToday(notification.timestamp)).length === 0 ? (
                    <p className="text-gray-600">No notifications this week</p>
                  ) : (
                    notifications
                      .filter(notification => !isToday(notification.timestamp))
                      .map((notification) => (
                        <div
                          key={notification.id}
                          className={`py-2 flex justify-between items-center ${
                            !notification.is_read ? 'bg-gray-800' : 'bg-gray-900'
                          } cursor-pointer`}
                          onClick={() => handleNotificationClick(notification)}
                        >
                          <div className="flex items-center">
                            <img
                              src="https://via.placeholder.com/40"
                              alt="User"
                              className="rounded-full h-8 w-8 mr-2"
                            />
                            <div>
                              <p className="font-semibold text-sm">{notification.message}</p>
                              <p className="text-xs text-gray-400">{new Date(notification.timestamp).toLocaleString()}</p>
                            </div>
                          </div>
                        </div>
                      ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default NotificationDropdown;