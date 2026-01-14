import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, DatePicker, Space, Typography, Divider, Alert, Tabs, Collapse, Select, Spin, Tooltip } from 'antd';
import { PlusOutlined, EyeOutlined, EditOutlined, QuestionCircleOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { CreateAssignmentDTO } from '../api/assignmentApi';
import { useAuth } from '../context/AuthContext';
import QuestionFormWithPreview, { QuestionData } from './QuestionFormWithPreview';
import DescriptionViewer from './DescriptionViewer';
import LatexQuickReference from './LatexQuickReference';
import { dockerImageApi, CustomDockerImage } from '../api/dockerImageApi';

const { TextArea } = Input;
const { Title } = Typography;
const { Option } = Select;

interface AssignmentFormWithPreviewProps {
    onSubmit: (values: CreateAssignmentDTO) => void;
    loading?: boolean;
    initialValues?: Partial<CreateAssignmentDTO>;
}

/**
 * Enhanced AssignmentForm with LaTeX-enabled Markdown preview
 * Teachers can write descriptions with LaTeX expressions and preview them in real-time
 */
const AssignmentFormWithPreview: React.FC<AssignmentFormWithPreviewProps> = ({
    onSubmit,
    loading = false,
    initialValues,
}) => {
    const [form] = Form.useForm();
    const { user } = useAuth();
    const [questions, setQuestions] = useState<QuestionData[]>([]);
    const [descriptionMode, setDescriptionMode] = useState<'edit' | 'preview'>('edit');
    const [descriptionValue, setDescriptionValue] = useState<string>(initialValues?.description || '');
    const [dockerImages, setDockerImages] = useState<CustomDockerImage[]>([]);
    const [loadingImages, setLoadingImages] = useState(false);

    // Fetch uploaded Docker images
    useEffect(() => {
        const fetchDockerImages = async () => {
            setLoadingImages(true);
            try {
                const images = await dockerImageApi.getUploaded();
                setDockerImages(images);
            } catch (error) {
                console.error('Failed to fetch Docker images:', error);
            } finally {
                setLoadingImages(false);
            }
        };

        fetchDockerImages();
    }, []);

    const handleAddQuestion = () => {
        const questionNumber = questions.length + 1;
        const newQuestion: QuestionData = {
            question_number: questionNumber,
            title: '',
            description: '',
            cell_id: `cell_${questionNumber}`,
            points: 10,
            starter_code: '# Write your code here\n',
        };
        setQuestions([...questions, newQuestion]);
    };

    const handleDeleteQuestion = (index: number) => {
        const updatedQuestions = questions.filter((_, i) => i !== index);
        const renumbered = updatedQuestions.map((q, i) => ({
            ...q,
            question_number: i + 1,
            cell_id: `cell_${i + 1}`,
        }));
        setQuestions(renumbered);
    };

    const handleMoveQuestion = (index: number, direction: 'up' | 'down') => {
        const newIndex = direction === 'up' ? index - 1 : index + 1;
        if (newIndex < 0 || newIndex >= questions.length) return;

        const updatedQuestions = [...questions];
        [updatedQuestions[index], updatedQuestions[newIndex]] =
            [updatedQuestions[newIndex], updatedQuestions[index]];

        const renumbered = updatedQuestions.map((q, i) => ({
            ...q,
            question_number: i + 1,
            cell_id: `cell_${i + 1}`,
        }));
        setQuestions(renumbered);
    };

    const handleQuestionChange = (index: number, updatedQuestion: QuestionData) => {
        const updatedQuestions = [...questions];
        updatedQuestions[index] = updatedQuestion;
        setQuestions(updatedQuestions);
    };

    const handleFinish = (values: any) => {
        const formattedValues: CreateAssignmentDTO = {
            title: values.title,
            description: values.description,
            questions: questions,
            teacher_id: user?.id || 'mock-teacher-id',
            due_date: values.due_date.toISOString(),
            custom_docker_image_id: values.custom_docker_image_id || null,
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
                    label="Assignment Description"
                    required
                >
                    <Tabs
                        activeKey={descriptionMode}
                        onChange={(key) => setDescriptionMode(key as 'edit' | 'preview')}
                        items={[
                            {
                                key: 'edit',
                                label: (
                                    <span>
                                        <EditOutlined /> Edit
                                    </span>
                                ),
                                children: (
                                    <Form.Item
                                        name="description"
                                        noStyle
                                        rules={[{ required: true, message: 'Please enter description' }]}
                                    >
                                        <TextArea
                                            rows={8}
                                            placeholder="Write overall assignment instructions in Markdown format...&#10;&#10;You can use LaTeX for math:&#10;- Inline: $x^2 + y^2 = z^2$&#10;- Display: $$\int_0^\infty e^{-x^2} dx$$"
                                            onChange={(e) => setDescriptionValue(e.target.value)}
                                        />
                                    </Form.Item>
                                ),
                            },
                            {
                                key: 'preview',
                                label: (
                                    <span>
                                        <EyeOutlined /> Preview
                                    </span>
                                ),
                                children: (
                                    <div
                                        style={{
                                            minHeight: '200px',
                                            padding: '12px',
                                            border: '1px solid #d9d9d9',
                                            borderRadius: '6px',
                                            backgroundColor: '#fafafa',
                                        }}
                                    >
                                        {descriptionValue ? (
                                            <DescriptionViewer content={descriptionValue} />
                                        ) : (
                                            <Typography.Text type="secondary">
                                                No content to preview. Switch to Edit tab to add description.
                                            </Typography.Text>
                                        )}
                                    </div>
                                ),
                            },
                        ]}
                    />
                    <Typography.Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                        Supports Markdown and LaTeX. Use $...$ for inline math and $$...$$ for display math.
                    </Typography.Text>
                </Form.Item>

                <Collapse
                    ghost
                    items={[
                        {
                            key: 'reference',
                            label: (
                                <Space>
                                    <QuestionCircleOutlined />
                                    <span>LaTeX Math Reference (click to expand)</span>
                                </Space>
                            ),
                            children: <LatexQuickReference />
                        }
                    ]}
                    style={{ marginBottom: 16 }}
                />

                <Form.Item
                    name="due_date"
                    label="Due Date"
                    rules={[{ required: true, message: 'Please select due date' }]}
                >
                    <DatePicker showTime style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                    name="custom_docker_image_id"
                    label={
                        <Space>
                            <span>Docker Image</span>
                            <Tooltip title="Select a custom Docker image with pre-installed packages. Leave empty to use the default Python image.">
                                <InfoCircleOutlined />
                            </Tooltip>
                        </Space>
                    }
                >
                    <Select
                        placeholder="Use Default Python Image"
                        allowClear
                        loading={loadingImages}
                        notFoundContent={loadingImages ? <Spin size="small" /> : 'No custom images available'}
                        style={{ width: '100%' }}
                    >
                        {dockerImages.map((image) => (
                            <Option key={image.id} value={image.id}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div>
                                        <strong>{image.name}</strong>
                                        <div style={{ fontSize: '12px', color: '#888' }}>
                                            {image.description || 'No description'}
                                        </div>
                                    </div>
                                    <div style={{ fontSize: '11px', color: '#666' }}>
                                        Base: {image.base_image}
                                    </div>
                                </div>
                            </Option>
                        ))}
                    </Select>
                </Form.Item>

                <Divider />

                <Title level={4}>Questions</Title>
                {questions.length === 0 && (
                    <Alert
                        message="No questions added yet"
                        description="Click the button below to add questions to this assignment."
                        type="info"
                        showIcon
                        style={{ marginBottom: 16 }}
                    />
                )}

                {questions.map((question, index) => (
                    <QuestionFormWithPreview
                        key={question.cell_id}
                        question={question}
                        onChange={(updated) => handleQuestionChange(index, updated)}
                        onDelete={() => handleDeleteQuestion(index)}
                        onMoveUp={() => handleMoveQuestion(index, 'up')}
                        onMoveDown={() => handleMoveQuestion(index, 'down')}
                        isFirst={index === 0}
                        isLast={index === questions.length - 1}
                    />
                ))}

                <Button
                    type="dashed"
                    icon={<PlusOutlined />}
                    onClick={handleAddQuestion}
                    block
                    style={{ marginBottom: 16 }}
                >
                    Add Question
                </Button>

                <Form.Item>
                    <Space>
                        <Button
                            type="primary"
                            htmlType="submit"
                            loading={loading}
                            disabled={questions.length === 0}
                        >
                            Create Assignment
                        </Button>
                        <Button onClick={() => {
                            form.resetFields();
                            setQuestions([]);
                            setDescriptionValue('');
                        }}>
                            Reset
                        </Button>
                    </Space>
                </Form.Item>
            </Form>
        </Card>
    );
};

export default AssignmentFormWithPreview;
