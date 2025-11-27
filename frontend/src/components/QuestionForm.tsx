import React from 'react';
import { Card, Input, InputNumber, Button, Space, Typography } from 'antd';
import { DeleteOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Text } = Typography;

export interface QuestionData {
  question_number: number;
  title: string;
  description: string;
  cell_id: string;
  points: number;
  starter_code?: string;
}

interface QuestionFormProps {
  question: QuestionData;
  onChange: (question: QuestionData) => void;
  onDelete: () => void;
  onMoveUp?: () => void;
  onMoveDown?: () => void;
  isFirst: boolean;
  isLast: boolean;
}

const QuestionForm: React.FC<QuestionFormProps> = ({
  question,
  onChange,
  onDelete,
  onMoveUp,
  onMoveDown,
  isFirst,
  isLast,
}) => {
  const handleChange = (field: keyof QuestionData, value: any) => {
    onChange({ ...question, [field]: value });
  };

  return (
    <Card
      size="small"
      title={
        <Space>
          <Text strong>Question {question.question_number}</Text>
          <Text type="secondary">(Cell ID: {question.cell_id})</Text>
        </Space>
      }
      extra={
        <Space>
          <Button
            size="small"
            icon={<ArrowUpOutlined />}
            onClick={onMoveUp}
            disabled={isFirst}
          />
          <Button
            size="small"
            icon={<ArrowDownOutlined />}
            onClick={onMoveDown}
            disabled={isLast}
          />
          <Button
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={onDelete}
          />
        </Space>
      }
      style={{ marginBottom: 16 }}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <div>
          <Text strong>Question Title *</Text>
          <Input
            placeholder="e.g., Calculate Circle Area"
            value={question.title}
            onChange={(e) => handleChange('title', e.target.value)}
            style={{ marginTop: 4 }}
          />
        </div>

        <div>
          <Text strong>Description (Markdown) *</Text>
          <TextArea
            placeholder="Write the question description in Markdown format..."
            value={question.description}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={4}
            style={{ marginTop: 4 }}
          />
        </div>

        <div>
          <Text strong>Points *</Text>
          <InputNumber
            min={0}
            value={question.points}
            onChange={(value) => handleChange('points', value || 0)}
            style={{ width: '100%', marginTop: 4 }}
          />
        </div>

        <div>
          <Text strong>Starter Code (Optional)</Text>
          <TextArea
            placeholder="# Write your code here"
            value={question.starter_code}
            onChange={(e) => handleChange('starter_code', e.target.value)}
            rows={3}
            style={{ marginTop: 4, fontFamily: 'monospace' }}
          />
        </div>
      </Space>
    </Card>
  );
};

export default QuestionForm;
