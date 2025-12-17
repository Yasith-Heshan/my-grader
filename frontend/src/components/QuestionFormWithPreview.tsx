import React, { useState } from 'react';
import { Card, Input, InputNumber, Button, Space, Typography, Tabs } from 'antd';
import { DeleteOutlined, ArrowUpOutlined, ArrowDownOutlined, EyeOutlined, EditOutlined } from '@ant-design/icons';
import DescriptionViewer from './DescriptionViewer';

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

interface QuestionFormWithPreviewProps {
  question: QuestionData;
  onChange: (question: QuestionData) => void;
  onDelete: () => void;
  onMoveUp?: () => void;
  onMoveDown?: () => void;
  isFirst: boolean;
  isLast: boolean;
}

/**
 * Enhanced QuestionForm with LaTeX-enabled Markdown preview
 * Teachers can write question descriptions with LaTeX expressions and preview them
 */
const QuestionFormWithPreview: React.FC<QuestionFormWithPreviewProps> = ({
  question,
  onChange,
  onDelete,
  onMoveUp,
  onMoveDown,
  isFirst,
  isLast,
}) => {
  const [descriptionMode, setDescriptionMode] = useState<'edit' | 'preview'>('edit');

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
          <Text strong>Description (Markdown with LaTeX) *</Text>
          <Tabs
            activeKey={descriptionMode}
            onChange={(key) => setDescriptionMode(key as 'edit' | 'preview')}
            size="small"
            items={[
              {
                key: 'edit',
                label: (
                  <span style={{ fontSize: '12px' }}>
                    <EditOutlined /> Edit
                  </span>
                ),
                children: (
                  <TextArea
                    placeholder="Write the question description in Markdown format...&#10;&#10;Example with LaTeX:&#10;Write a function to calculate $A = \pi r^2$"
                    value={question.description}
                    onChange={(e) => handleChange('description', e.target.value)}
                    rows={4}
                    style={{ fontFamily: 'monospace' }}
                  />
                ),
              },
              {
                key: 'preview',
                label: (
                  <span style={{ fontSize: '12px' }}>
                    <EyeOutlined /> Preview
                  </span>
                ),
                children: (
                  <div
                    style={{
                      minHeight: '100px',
                      padding: '8px',
                      border: '1px solid #d9d9d9',
                      borderRadius: '4px',
                      backgroundColor: '#fafafa',
                    }}
                  >
                    {question.description ? (
                      <DescriptionViewer content={question.description} />
                    ) : (
                      <Typography.Text type="secondary" style={{ fontSize: '12px' }}>
                        No content to preview
                      </Typography.Text>
                    )}
                  </div>
                ),
              },
            ]}
          />
          <Typography.Text type="secondary" style={{ fontSize: '11px', display: 'block', marginTop: '4px' }}>
            Use $...$ for inline math (e.g., $x^2$) and $$...$$ for display math
          </Typography.Text>
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

export default QuestionFormWithPreview;
