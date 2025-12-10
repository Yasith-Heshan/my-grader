import React, { createContext, useContext, useState, useEffect } from 'react';
import { userApi } from '../api/userApi';
import axiosInstance from '../api/axiosInstance';
import { useStoreActions } from '../store';

interface User {
    id: string;
    name: string;
    email: string;
    role: 'teacher' | 'student';
}

interface AuthContextType {
    user: User | null;
    login: (email: string, password: string, role: 'teacher' | 'student') => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
    initialized: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [initialized, setInitialized] = useState(false);
    const setCurrentUser = useStoreActions((actions) => actions.user.setCurrentUser);

    // Load user from token/backend on mount
    useEffect(() => {
        const init = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                setInitialized(true);
                return;
            }
            // set axios default header immediately so calls use the token
            axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;

            try {
                const data = await userApi.getCurrentUser();
                setUser(data);
                setCurrentUser(data);
                localStorage.setItem('user', JSON.stringify(data));
            } catch (err) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                setUser(null);
                setCurrentUser(null);
            } finally {
                setInitialized(true);
            }
        };
        init();
    }, []);

    const login = async (email: string, password: string, role: 'teacher' | 'student') => {
        try {
            const resp = await userApi.login({ email, password, role });
            const { user, token } = resp;
            setUser(user);
            setCurrentUser(user);
            localStorage.setItem('user', JSON.stringify(user));
            localStorage.setItem('token', token);
            // set axios default header for immediate authenticated requests
            axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            setInitialized(true);
        } catch (err) {
            throw err;
        }
    };

    const logout = async () => {
        try {
            await userApi.logout();
        } catch (err) {
            // ignore server logout errors
        }
        setUser(null);
        setCurrentUser(null);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        delete axiosInstance.defaults.headers.common['Authorization'];
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user, initialized }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        // Fail-safe: return a harmless default to avoid app crash when used outside provider
        // This prevents a blank/gray screen caused by thrown errors in dev builds.
        // Log a warning to help debugging.
        // eslint-disable-next-line no-console
        console.warn('useAuth called outside AuthProvider — returning fallback values');
        return {
            user: null,
            login: async () => {
                throw new Error('Auth not initialized');
            },
            logout: () => {},
            isAuthenticated: false,
            initialized: true,
        } as AuthContextType;
    }
    return context;
};
