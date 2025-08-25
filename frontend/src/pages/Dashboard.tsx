import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8\">
      <div className=\"mb-8\">
        <h1 className=\"text-3xl font-bold text-gray-900\">Dashboard</h1>
        <p className=\"mt-2 text-gray-600\">
          Welcome to your AI Learning Platform dashboard. Track your progress and continue learning.
        </p>
      </div>

      {/* Dashboard content will go here */}
      <div className=\"grid grid-cols-1 lg:grid-cols-3 gap-8\">
        <div className=\"lg:col-span-2\">
          <div className=\"card\">
            <h2 className=\"text-lg font-semibold text-gray-900 mb-4\">Recent Activity</h2>
            <div className=\"text-gray-500\">
              Your recent learning activities will appear here.
            </div>
          </div>
        </div>

        <div className=\"space-y-6\">
          <div className=\"card\">
            <h3 className=\"text-lg font-semibold text-gray-900 mb-4\">Study Streak</h3>
            <div className=\"text-center\">
              <div className=\"text-3xl font-bold text-primary-600\">0</div>
              <div className=\"text-sm text-gray-500\">Days in a row</div>
            </div>
          </div>

          <div className=\"card\">
            <h3 className=\"text-lg font-semibold text-gray-900 mb-4\">Quick Actions</h3>
            <div className=\"space-y-3\">
              <button className=\"w-full btn btn-primary text-left\">
                Upload Document
              </button>
              <button className=\"w-full btn btn-outline text-left\">
                Start AI Chat
              </button>
              <button className=\"w-full btn btn-outline text-left\">
                View Progress
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
