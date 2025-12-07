import React, { createContext, useContext, useState, useEffect } from 'react';
import { userApi } from '../api/userApi';

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
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);

    // Load user from token/backend on mount
    useEffect(() => {
        const init = async () => {
            const token = localStorage.getItem('token');
            if (!token) return;
            try {
                const data = await userApi.getCurrentUser();
                setUser(data);
                localStorage.setItem('user', JSON.stringify(data));
            } catch (err) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                setUser(null);
            }
        };
        init();
    }, []);

    const login = async (email: string, password: string, role: 'teacher' | 'student') => {
        try {
            const resp = await userApi.login({ email, password, role });
            const { user, token } = resp;
            setUser(user);
            localStorage.setItem('user', JSON.stringify(user));
            localStorage.setItem('token', token);
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
        localStorage.removeItem('user');
        localStorage.removeItem('token');
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};
