import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Typography, Space } from 'antd';
import { UserOutlined, LockOutlined, LoginOutlined } from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';

const { Title, Text } = Typography;

const LoginPage: React.FC = () => {
    const [form] = Form.useForm();
    const navigate = useNavigate();
    const { login } = useAuth();
    const [loading, setLoading] = useState(false);

    const handleLogin = async (values: { email: string; password: string }) => {
        setLoading(true);
        try {
            const loggedInUser = await login(values.email, values.password);
            setLoading(false);
            // Redirect based on role
            if (loggedInUser.role === 'teacher') navigate('/teacher');
            else navigate('/student');
        } catch (err: any) {
            setLoading(false);
            toast.error(err.response?.data?.detail || err.message || 'Login failed');
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}>
            <Card
                style={{
                    width: 450,
                    boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
                }}
            >
                <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center' }}>
                    <div>
                        <Title level={2} style={{ marginBottom: 8 }}>Welcome Back</Title>
                        <Text type="secondary">Sign in to continue to Grading System</Text>
                    </div>

                    <Form
                        form={form}
                        onFinish={handleLogin}
                        layout="vertical"
                        size="large"
                    >
                        <Form.Item
                            name="email"
                            label="Email"
                            rules={[
                                { required: true, message: 'Please enter your email' },
                                { type: 'email', message: 'Please enter a valid email' }
                            ]}
                        >
                            <Input
                                prefix={<UserOutlined />}
                                placeholder="Enter your email"
                            />
                        </Form.Item>

                        <Form.Item
                            name="password"
                            label="Password"
                            rules={[{ required: true, message: 'Please enter your password' }]}
                        >
                            <Input.Password
                                prefix={<LockOutlined />}
                                placeholder="Enter your password"
                            />
                        </Form.Item>

                        {/* Role no longer required — backend derives from account */}

                        <Form.Item style={{ marginBottom: 0 }}>
                            <Button
                                type="primary"
                                htmlType="submit"
                                icon={<LoginOutlined />}
                                loading={loading}
                                block
                            >
                                Sign In
                            </Button>
                        </Form.Item>
                    </Form>

                    <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                            Don't have an account?
                        </Text>
                        <Link to="/register">Create account</Link>
                    </div>
                </Space>
            </Card>
        </div>
    );
};

export default LoginPage;
