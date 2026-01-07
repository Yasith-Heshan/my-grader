import React from 'react';
import { Layout, Menu, Button, Space, Typography } from 'antd';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  HomeOutlined,
  BookOutlined,
  FileTextOutlined,
  LogoutOutlined,
  UserOutlined,
  DockerOutlined,
} from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';

const { Header } = Layout;
const { Text } = Typography;

const Navbar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user: currentUser, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const teacherMenuItems = [
    {
      key: '/teacher',
      icon: <HomeOutlined />,
      label: <Link to="/teacher">Dashboard</Link>,
    },
    {
      key: '/teacher/summary',
      icon: <FileTextOutlined />,
      label: <Link to="/teacher/summary">Summary</Link>,
    },
    {
      key: '/teacher/docker-images',
      icon: <DockerOutlined />,
      label: <Link to="/teacher/docker-images">Docker Images</Link>,
    },
    {
      key: '/profile',
      icon: <UserOutlined />,
      label: <Link to="/profile">Profile</Link>,
    },
    {
      key: '/users',
      icon: <UserOutlined />,
      label: <Link to="/users">Users</Link>,
    },
  ];

  const studentMenuItems = [
    {
      key: '/student',
      icon: <HomeOutlined />,
      label: <Link to="/student">Dashboard</Link>,
    },
    {
      key: '/assignments',
      icon: <BookOutlined />,
      label: <Link to="/student">Assignments</Link>,
    },
    {
      key: '/profile',
      icon: <UserOutlined />,
      label: <Link to="/profile">Profile</Link>,
    },
    {
      key: '/users',
      icon: <UserOutlined />,
      label: <Link to="/users">Users</Link>,
    },
  ];

  const menuItems = currentUser?.role === 'teacher' ? teacherMenuItems : studentMenuItems;

  return (
    <Header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        background: '#001529',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
        <div
          style={{
            color: 'white',
            fontSize: '20px',
            fontWeight: 'bold',
            cursor: 'pointer',
          }}
          onClick={() => navigate('/')}
        >
          📓 Notebook Grader
        </div>
        {currentUser && (
          <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            style={{ minWidth: 200, background: 'transparent' }}
          />
        )}
      </div>

      {currentUser && (
        <Space>
          <UserOutlined style={{ color: 'white' }} />
          <Text style={{ color: 'white' }}>
            {currentUser.name} ({currentUser.role})
          </Text>
          <Button type="primary" danger icon={<LogoutOutlined />} onClick={handleLogout}>
            Logout
          </Button>
        </Space>
      )}
    </Header>
  );
};

export default Navbar;
