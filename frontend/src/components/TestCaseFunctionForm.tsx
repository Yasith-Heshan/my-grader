import React, { useState } from 'react';
import { Modal, Form, Input, InputNumber, Button, Space, Typography } from 'antd';
import Editor from '@monaco-editor/react';
import { CreateTestCaseDTO } from '../api/testCaseApi';
import { useCreateTestCase } from '../hooks/useTestCases';

const { TextArea } = Input;
const { Title, Text } = Typography;

interface TestCaseFunctionFormProps {
    visible: boolean;
    onClose: () => void;
    assignmentId: string;
}

const defaultTestCaseFunction = `def test_function(submission):
    """
    Test function template
    
    Args:
        submission: Dictionary containing student's executed code namespace
                   e.g., {'function_name': <function>, 'variable': value}
    
    Returns:
        dict: {"score": float (0-1), "feedback": string}
    
    Example:
        if 'my_function' not in submission:
            return {"score": 0, "feedback": "Function not found"}
        
        func = submission['my_function']
        result = func(test_input)
        
        if result == expected:
            return {"score": 1.0, "feedback": "✅ Correct!"}
        else:
            return {"score": 0.0, "feedback": f"❌ Expected {expected}, got {result}"}
    """
    # TODO: Implement your test logic here
    return {"score": 0, "feedback": "Test not implemented"}
`;

const TestCaseFunctionForm: React.FC<TestCaseFunctionFormProps> = ({
    visible,
    onClose,
    assignmentId,
}) => {
    const [form] = Form.useForm();
    const createMutation = useCreateTestCase();
    const [testcaseFunction, setTestcaseFunction] = useState(defaultTestCaseFunction);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();

            const data: CreateTestCaseDTO = {
                assignment_id: assignmentId,
                question_number: values.question_number,
                cell_id: values.cell_id,
                testcase_name: values.testcase_name,
                testcase_function: testcaseFunction,
                timeout: values.timeout || 5,
                language: values.language || 'python',
                points: values.points || 1.0,
                description: values.description || null,
            };

            createMutation.mutate(data, {
                onSuccess: () => {
                    form.resetFields();
                    setTestcaseFunction(defaultTestCaseFunction);
                    onClose();
                },
            });
        } catch (error) {
            console.error('Form validation failed:', error);
        }
    };

    const handleCancel = () => {
        form.resetFields();
        setTestcaseFunction(defaultTestCaseFunction);
        onClose();
    };

    return (
        <Modal
            title={<Title level={4}>Add Test Case Function</Title>}
            open={visible}
            onCancel={handleCancel}
            width={900}
            footer={[
                <Button key="cancel" onClick={handleCancel}>
                    Cancel
                </Button>,
                <Button
                    key="submit"
                    type="primary"
                    loading={createMutation.isPending}
                    onClick={handleSubmit}
                >
                    Create Test Case
                </Button>,
            ]}
        >
            <Form
                form={form}
                layout="vertical"
                initialValues={{
                    timeout: 5,
                    language: 'python',
                    points: 10.0,
                }}
            >
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                    <div>
                        <Form.Item
                            name="testcase_name"
                            label="Test Case Name"
                            rules={[{ required: true, message: 'Please enter test case name' }]}
                        >
                            <Input placeholder="e.g., test_circle_area" />
                        </Form.Item>

                        <Space style={{ width: '100%' }}>
                            <Form.Item
                                name="question_number"
                                label="Question Number"
                                rules={[{ required: true, message: 'Required' }]}
                                style={{ width: 150 }}
                            >
                                <InputNumber min={1} placeholder="1" style={{ width: '100%' }} />
                            </Form.Item>

                            <Form.Item
                                name="cell_id"
                                label="Cell ID"
                                rules={[{ required: true, message: 'Required' }]}
                                style={{ width: 200 }}
                            >
                                <Input placeholder="e.g., cell_1" />
                            </Form.Item>

                            <Form.Item
                                name="points"
                                label="Points"
                                style={{ width: 120 }}
                            >
                                <InputNumber min={0} step={0.5} style={{ width: '100%' }} />
                            </Form.Item>

                            <Form.Item
                                name="timeout"
                                label="Timeout (seconds)"
                                style={{ width: 150 }}
                            >
                                <InputNumber min={1} max={60} style={{ width: '100%' }} />
                            </Form.Item>
                        </Space>
                    </div>

                    <div>
                        <Form.Item label="Test Function (Python)">
                            <Text type="secondary" style={{ fontSize: '12px' }}>
                                Write a function that receives the student's code namespace and returns a score (0-1) and feedback.
                            </Text>
                            <div style={{ marginTop: 8, border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                                <Editor
                                    height="400px"
                                    defaultLanguage="python"
                                    language="python"
                                    value={testcaseFunction}
                                    onChange={(value) => setTestcaseFunction(value || '')}
                                    theme="vs-dark"
                                    options={{
                                        minimap: { enabled: false },
                                        fontSize: 14,
                                        lineNumbers: 'on',
                                        scrollBeyondLastLine: false,
                                        automaticLayout: true,
                                    }}
                                />
                            </div>
                        </Form.Item>
                    </div>

                    <Form.Item
                        name="description"
                        label="Description (optional)"
                    >
                        <TextArea
                            rows={2}
                            placeholder="Additional information about this test case..."
                        />
                    </Form.Item>
                </Space>
            </Form>
        </Modal>
    );
};

export default TestCaseFunctionForm;
