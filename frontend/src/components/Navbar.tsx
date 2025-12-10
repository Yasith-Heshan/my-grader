import React from 'react';
import { Layout, Menu, Button, Space, Typography } from 'antd';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  HomeOutlined,
  BookOutlined,
  FileTextOutlined,
  LogoutOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { useStoreState } from '../store';
import { useLogout } from '../hooks/useUser';

const { Header } = Layout;
const { Text } = Typography;

const Navbar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const currentUser = useStoreState((state) => state.user.currentUser);
  const logoutMutation = useLogout();

  const handleLogout = () => {
    logoutMutation.mutate();
  };

  const teacherMenuItems = [
    {
      key: '/teacher',
      icon: <HomeOutlined />,
      label: <Link to="/teacher">Dashboard</Link>,
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
          <Button
            type="primary"
            danger
            icon={<LogoutOutlined />}
            onClick={handleLogout}
            loading={logoutMutation.isPending}
          >
            Logout
          </Button>
        </Space>
      )}
    </Header>
  );
};

export default Navbar;
