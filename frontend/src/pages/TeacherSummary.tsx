import React from 'react';
import { Card, Typography } from 'antd';

const { Title, Paragraph } = Typography;

const TeacherSummary: React.FC = () => {
  return (
    <div style={{ padding: 24 }}>
      <Card>
        <Title level={3}>Teacher Summary</Title>
        <Paragraph>This page will show assignment summaries, grading stats and reports.</Paragraph>
      </Card>
    </div>
  );
};

export default TeacherSummary;
