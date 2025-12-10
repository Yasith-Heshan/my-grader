import React from 'react';
import { Card, Button, Typography } from 'antd';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;

const Profile: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (!user) {
    return null;
  }

  return (
    <div style={{ padding: 24 }}>
      <Card style={{ maxWidth: 600 }}>
        <Title level={3}>Profile</Title>
        <div style={{ marginBottom: 12 }}>
          <Text strong>Name: </Text> <Text>{user.name}</Text>
        </div>
        <div style={{ marginBottom: 12 }}>
          <Text strong>Email: </Text> <Text>{user.email}</Text>
        </div>
        <div style={{ marginBottom: 12 }}>
          <Text strong>Role: </Text> <Text>{user.role}</Text>
        </div>
        <Button danger onClick={handleLogout}>Logout</Button>
      </Card>
    </div>
  );
};

export default Profile;
