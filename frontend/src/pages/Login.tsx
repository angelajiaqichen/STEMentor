import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate(from, { replace: true });
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className=\"min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8\">
      <div className=\"max-w-md w-full space-y-8\">
        <div>
          <div className=\"mx-auto h-12 w-12 bg-primary-600 rounded-lg flex items-center justify-center\">
            <span className=\"text-white font-bold text-lg\">AI</span>
          </div>
          <h2 className=\"mt-6 text-center text-3xl font-extrabold text-gray-900\">
            Sign in to your account
          </h2>
          <p className=\"mt-2 text-center text-sm text-gray-600\">
            Or{' '}
            <Link
              to=\"/register\"
              className=\"font-medium text-primary-600 hover:text-primary-500\"
            >
              create a new account
            </Link>
          </p>
        </div>
        
        <form className=\"mt-8 space-y-6\" onSubmit={handleSubmit}>
          <div className=\"space-y-4\">
            <div>
              <label htmlFor=\"email\" className=\"block text-sm font-medium text-gray-700\">
                Email address
              </label>
              <input
                id=\"email\"
                name=\"email\"
                type=\"email\"
                autoComplete=\"email\"
                required
                className=\"input mt-1\"
                placeholder=\"Enter your email\"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            
            <div>
              <label htmlFor=\"password\" className=\"block text-sm font-medium text-gray-700\">
                Password
              </label>
              <input
                id=\"password\"
                name=\"password\"
                type=\"password\"
                autoComplete=\"current-password\"
                required
                className=\"input mt-1\"
                placeholder=\"Enter your password\"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className=\"flex items-center justify-between\">
            <div className=\"text-sm\">
              <a href=\"#\" className=\"font-medium text-primary-600 hover:text-primary-500\">
                Forgot your password?
              </a>
            </div>
          </div>

          <div>
            <button
              type=\"submit\"
              disabled={isLoading}
              className=\"w-full btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed\"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
