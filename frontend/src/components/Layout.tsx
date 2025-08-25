import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  DocumentTextIcon, 
  ChatBubbleLeftRightIcon, 
  ChartBarIcon,
  Bars3Icon,
  XMarkIcon,
  UserIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Documents', href: '/documents', icon: DocumentTextIcon },
  { name: 'AI Tutor', href: '/chat', icon: ChatBubbleLeftRightIcon },
  { name: 'Progress', href: '/progress', icon: ChartBarIcon },
];

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className=\"flex h-screen bg-gray-50\">
      {/* Mobile sidebar */}
      {sidebarOpen && (
        <div className=\"fixed inset-0 z-40 lg:hidden\">
          <div 
            className=\"fixed inset-0 bg-gray-600 bg-opacity-75\"
            onClick={() => setSidebarOpen(false)}
          />
          <nav className=\"fixed top-0 left-0 bottom-0 flex flex-col w-5/6 max-w-sm bg-white shadow-xl\">
            <div className=\"absolute top-0 right-0 -mr-12 pt-2\">
              <button
                type=\"button\"
                className=\"ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white\"
                onClick={() => setSidebarOpen(false)}
              >
                <XMarkIcon className=\"h-6 w-6 text-white\" />
              </button>
            </div>
            <div className=\"flex-shrink-0 px-4 py-4 flex items-center\">
              <div className=\"flex items-center\">
                <div className=\"flex-shrink-0\">
                  <div className=\"h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center\">
                    <span className=\"text-white font-bold text-sm\">AI</span>
                  </div>
                </div>
                <div className=\"ml-3\">
                  <h1 className=\"text-lg font-semibold text-gray-900\">Learning Platform</h1>
                </div>
              </div>
            </div>
            <nav className=\"mt-8 flex-1 px-4 space-y-1\">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-2 py-2 text-base font-medium rounded-md transition-colors ${
                    location.pathname === item.href
                      ? 'bg-primary-100 text-primary-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className=\"mr-4 h-6 w-6\" />
                  {item.name}
                </Link>
              ))}
            </nav>
          </nav>
        </div>
      )}

      {/* Desktop sidebar */}
      <div className=\"hidden lg:flex lg:flex-shrink-0\">
        <div className=\"flex flex-col w-64 bg-white border-r border-gray-200\">
          <div className=\"flex items-center h-16 flex-shrink-0 px-4 bg-white\">
            <div className=\"flex items-center\">
              <div className=\"flex-shrink-0\">
                <div className=\"h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center\">
                  <span className=\"text-white font-bold text-sm\">AI</span>
                </div>
              </div>
              <div className=\"ml-3\">
                <h1 className=\"text-lg font-semibold text-gray-900\">Learning Platform</h1>
              </div>
            </div>
          </div>
          <nav className=\"mt-8 flex-1 px-4 space-y-1\">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                  location.pathname === item.href
                    ? 'bg-primary-100 text-primary-900'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <item.icon className=\"mr-3 h-5 w-5\" />
                {item.name}
              </Link>
            ))}
          </nav>
          
          {/* User menu */}
          <div className=\"flex-shrink-0 flex border-t border-gray-200 p-4\">
            <div className=\"flex-shrink-0 w-full group block\">
              <div className=\"flex items-center justify-between\">
                <div className=\"flex items-center\">
                  <div>
                    <div className=\"inline-block h-9 w-9 rounded-full bg-gray-200 flex items-center justify-center\">
                      <UserIcon className=\"h-5 w-5 text-gray-500\" />
                    </div>
                  </div>
                  <div className=\"ml-3\">
                    <p className=\"text-sm font-medium text-gray-700 group-hover:text-gray-900\">
                      {user?.name || user?.email}
                    </p>
                    <p className=\"text-xs font-medium text-gray-500 group-hover:text-gray-700\">
                      View profile
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className=\"ml-3 inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded text-gray-700 bg-gray-100 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500\"
                >
                  <ArrowRightOnRectangleIcon className=\"h-4 w-4\" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className=\"flex flex-col w-0 flex-1 overflow-hidden\">
        <div className=\"relative z-10 flex-shrink-0 flex h-16 bg-white shadow lg:hidden\">
          <button
            type=\"button\"
            className=\"px-4 border-r border-gray-200 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 lg:hidden\"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className=\"h-6 w-6\" />
          </button>
        </div>

        <main className=\"flex-1 relative overflow-y-auto focus:outline-none\">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
