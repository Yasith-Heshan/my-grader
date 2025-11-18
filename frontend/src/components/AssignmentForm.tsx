import React from 'react';
import { Form, Input, Button, Card, DatePicker, Space, InputNumber } from 'antd';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { CreateAssignmentDTO } from '../api/assignmentApi';
import dayjs from 'dayjs';

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

  const handleFinish = (values: any) => {
    const formattedValues = {
      ...values,
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

        <Form.Item label="Test Cases">
          <Form.List name="test_cases">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Card
                    key={key}
                    size="small"
                    style={{ marginBottom: 16 }}
                    extra={
                      <MinusCircleOutlined
                        onClick={() => remove(name)}
                        style={{ color: 'red' }}
                      />
                    }
                  >
                    <Form.Item
                      {...restField}
                      name={[name, 'name']}
                      label="Test Case Name"
                      rules={[{ required: true, message: 'Enter test name' }]}
                    >
                      <Input placeholder="e.g., Test Basic Function" />
                    </Form.Item>

                    <Form.Item
                      {...restField}
                      name={[name, 'code']}
                      label="Test Code"
                      rules={[{ required: true, message: 'Enter test code' }]}
                    >
                      <TextArea
                        rows={3}
                        placeholder="e.g., assert add(2, 3) == 5"
                      />
                    </Form.Item>

                    <Form.Item
                      {...restField}
                      name={[name, 'expected_output']}
                      label="Expected Output (optional)"
                    >
                      <Input placeholder="Expected console output" />
                    </Form.Item>

                    <Form.Item
                      {...restField}
                      name={[name, 'points']}
                      label="Points"
                      rules={[{ required: true, message: 'Enter points' }]}
                    >
                      <InputNumber min={0} style={{ width: '100%' }} />
                    </Form.Item>
                  </Card>
                ))}
                <Button
                  type="dashed"
                  onClick={() => add()}
                  block
                  icon={<PlusOutlined />}
                >
                  Add Test Case
                </Button>
              </>
            )}
          </Form.List>
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
