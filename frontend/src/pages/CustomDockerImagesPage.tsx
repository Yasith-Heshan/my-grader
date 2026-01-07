import React from 'react';
import { Layout, Typography } from 'antd';
import CustomDockerImageManager from '../components/CustomDockerImageManager';

const { Content } = Layout;
const { Title } = Typography;

const CustomDockerImagesPage: React.FC = () => {
  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Content style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
        <CustomDockerImageManager />
      </Content>
    </Layout>
  );
};

export default CustomDockerImagesPage;
