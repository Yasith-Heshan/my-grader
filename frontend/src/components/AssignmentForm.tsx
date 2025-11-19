import React from 'react';
import { Form, Input, Button, Card, DatePicker, Space } from 'antd';
import { CreateAssignmentDTO } from '../api/assignmentApi';
import { useAuth } from '../context/AuthContext';

const { TextArea } = Input;

interface AssignmentFormProps {
  onSubmit: (values: CreateAssignmentDTO) => void;
  loading?: boolean;
  initialValues?: Partial<CreateAssignmentDTO>;
}

const AssignmentForm: React.FC<AssignmentFormProps> = ({
  onSubmit,
  loading = false,
  initialValues,
}) => {
  const [form] = Form.useForm();
  const { user } = useAuth();

  const handleFinish = (values: any) => {
    const formattedValues: CreateAssignmentDTO = {
      title: values.title,
      description: values.description,
      teacher_id: user?.id || 'mock-teacher-id',
      due_date: values.due_date.toISOString(),
    };
    onSubmit(formattedValues);
  };

  return (
    <Card title="Create New Assignment">
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        initialValues={initialValues}
      >
        <Form.Item
          name="title"
          label="Assignment Title"
          rules={[{ required: true, message: 'Please enter assignment title' }]}
        >
          <Input placeholder="e.g., Python Functions Assignment" />
        </Form.Item>

        <Form.Item
          name="description"
          label="Description"
          rules={[{ required: true, message: 'Please enter description' }]}
        >
          <TextArea
            rows={4}
            placeholder="Write assignment instructions in Markdown format..."
          />
        </Form.Item>

        <Form.Item
          name="due_date"
          label="Due Date"
          rules={[{ required: true, message: 'Please select due date' }]}
        >
          <DatePicker showTime style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" loading={loading}>
              Create Assignment
            </Button>
            <Button onClick={() => form.resetFields()}>Reset</Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default AssignmentForm;
