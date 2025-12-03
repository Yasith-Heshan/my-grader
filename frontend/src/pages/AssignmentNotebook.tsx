import React, { useState, useEffect } from 'react';
import { Layout, Card, Button, Typography, Space, Tag, Divider, Alert, Spin, Modal, Table } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import { CalendarOutlined, SendOutlined, PlayCircleOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { useAssignment } from '../hooks/useAssignments';
import { useCreateSubmission } from '../hooks/useSubmissions';
import CodeEditor from '../components/CodeEditor';
import axiosInstance from '../api/axiosInstance';
import { toast } from 'react-toastify';
import { Question } from '../api/assignmentApi';

const { Content } = Layout;
const { Title, Text, Paragraph } = Typography;

interface CellAnswer {
  cell_id: string;
  code: string;
}

interface TestResult {
  testcase_name: string;
  cell_id: string;
  score: number;
  max_score: number;
  feedback: string;
  passed: boolean;
}

interface QuestionCellProps {
  question: Question;
  code: string;
  onCodeChange: (code: string) => void;
  onRun: () => void;
  onTest: () => void;
  running: boolean;
  testing: boolean;
  output?: string;
  error?: string;
  onShiftEnter?: () => void;
}

const QuestionCell: React.FC<QuestionCellProps> = ({
  question,
  code,
  onCodeChange,
  onRun,
  onTest,
  running,
  testing,
  output,
  error,
  onShiftEnter,
}) => {
  return (
    <Card
      style={{ marginBottom: 24, border: '1px solid #e8e8e8' }}
      bodyStyle={{ padding: 0 }}
    >
      {/* Markdown Cell */}
      <div style={{
        padding: '16px 24px',
        background: '#fafafa',
        borderBottom: '1px solid #e8e8e8',
      }}>
        <Space direction="vertical" style={{ width: '100%' }} size="small">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Title level={5} style={{ margin: 0, color: '#1890ff' }}>
              Question {question.question_number}: {question.title}
            </Title>
            <Tag color="blue">{question.points} points</Tag>
          </div>
          <div style={{
            padding: '12px',
            background: 'white',
            borderRadius: '4px',
            border: '1px solid #d9d9d9',
          }}>
            <ReactMarkdown>{question.description}</ReactMarkdown>
          </div>
        </Space>
      </div>

      {/* Code Cell */}
      <div style={{ padding: '16px 24px' }}>
        <div style={{
          marginBottom: 8,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <Text type="secondary" style={{ fontFamily: 'monospace', fontSize: 12 }}>
            In [{question.question_number}]:
          </Text>
          <Space>
            <Button
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={onRun}
              loading={running}
            >
              Run
            </Button>
            <Button
              size="small"
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={onTest}
              loading={testing}
            >
              Run Tests
            </Button>
          </Space>
        </div>
        <div
          style={{
            border: '1px solid #d9d9d9',
            borderRadius: '4px',
            overflow: 'hidden',
          }}
          data-cell-id={question.cell_id}
        >
          <CodeEditor
            value={code}
            onChange={(value) => onCodeChange(value || '')}
            height="200px"
            onCtrlEnter={onRun}
            onShiftEnter={() => {
              onRun();
              if (onShiftEnter) {
                setTimeout(() => onShiftEnter(), 100);
              }
            }}
          />
        </div>

        {/* Output Display */}
        {(output || error) && (
          <div style={{ marginTop: 12 }}>
            <Text type="secondary" style={{ fontFamily: 'monospace', fontSize: 12 }}>
              Output:
            </Text>
            <div style={{
              marginTop: 4,
              padding: '12px',
              background: error ? '#fff2f0' : '#f6f6f6',
              border: `1px solid ${error ? '#ffccc7' : '#d9d9d9'}`,
              borderRadius: '4px',
              fontFamily: 'monospace',
              fontSize: '13px',
              whiteSpace: 'pre-wrap',
              maxHeight: '200px',
              overflowY: 'auto',
            }}>
              {error ? (
                <Text type="danger">{error}</Text>
              ) : (
                <Text>{output}</Text>
              )}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

const AssignmentNotebook: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [answers, setAnswers] = useState<Map<string, string>>(new Map());
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [testing, setTesting] = useState(false);
  const [testingCell, setTestingCell] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [runningCell, setRunningCell] = useState<string | null>(null);
  const [cellOutputs, setCellOutputs] = useState<Map<string, { output?: string; error?: string }>>(new Map());
  const [showResults, setShowResults] = useState(false);

  // Shared notebook state - variables persist across cells
  const [notebookVariables, setNotebookVariables] = useState<any>({});
  const [notebookFunctions, setNotebookFunctions] = useState<any>({});

  const { data: assignment, isLoading } = useAssignment(id || '');
  const submitMutation = useCreateSubmission();

  // Initialize answers with starter code
  useEffect(() => {
    if (assignment?.questions && assignment.questions.length > 0) {
      const initialAnswers = new Map<string, string>();
      assignment.questions.forEach(q => {
        initialAnswers.set(q.cell_id, q.starter_code || '# Write your code here\n');
      });
      setAnswers(initialAnswers);
    }
  }, [assignment]);

  const handleCodeChange = (cellId: string, code: string) => {
    setAnswers(new Map(answers.set(cellId, code)));
  };

  const focusNextCell = (currentCellId: string) => {
    const questionsList = assignment?.questions || [];
    const currentIndex = questionsList.findIndex(q => q.cell_id === currentCellId);
    if (currentIndex >= 0 && currentIndex < questionsList.length - 1) {
      // Focus next cell by finding the next editor
      const nextCellId = questionsList[currentIndex + 1].cell_id;
      // Try to focus the next cell's editor
      setTimeout(() => {
        const nextEditor = document.querySelector(`[data-cell-id="${nextCellId}"]`);
        if (nextEditor) {
          (nextEditor as HTMLElement).focus();
        }
      }, 150);
    }
  };

  const handleRunCell = async (cellId: string) => {
    setRunningCell(cellId);
    setRunning(true);

    try {
      const code = answers.get(cellId) || '';

      // Create a console capture
      const outputs: string[] = [];
      const errors: string[] = [];

      // Create a simple print function
      const print = (...args: any[]) => {
        outputs.push(args.map(arg =>
          typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
        ).join(' '));
      };

      try {
        // Use shared notebook variables and functions
        const variables = { ...notebookVariables };
        const functions = { ...notebookFunctions };

        const executionContext: any = {
          print,
          console: {
            log: print,
            error: (...args: any[]) => errors.push(args.join(' ')),
          },
          // Add common Python functions
          len: (arr: any) => Array.isArray(arr) || typeof arr === 'string' ? arr.length : 0,
          range: (start: number, end?: number, step: number = 1) => {
            if (end === undefined) { end = start; start = 0; }
            const result = [];
            for (let i = start; i < end; i += step) result.push(i);
            return result;
          },
          sum: (arr: number[]) => arr.reduce((a, b) => a + b, 0),
          max: (...args: any[]) => Math.max(...args.flat()),
          min: (...args: any[]) => Math.min(...args.flat()),
          abs: Math.abs,
          round: Math.round,
          Math,
          ...functions, // Include previously defined functions
        };

        // Parse and execute line by line
        const lines = code.trim().split('\n');

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i].trim();
          if (!line || line.startsWith('#')) continue;

          try {
            // Check if it's an assignment
            if (line.includes('=') && !line.includes('==') && !line.includes('!=') && !line.includes('<=') && !line.includes('>=')) {
              const match = line.match(/^(\w+)\s*=\s*(.+)$/);
              if (match) {
                const varName = match[1];
                let value = match[2];

                // Convert Python literals
                value = value
                  .replace(/^'([^']*)'$/, '"$1"')
                  .replace(/^"([^"]*)"$/, '"$1"')
                  .replace(/\bTrue\b/g, 'true')
                  .replace(/\bFalse\b/g, 'false')
                  .replace(/\bNone\b/g, 'null');

                // Evaluate the value with access to all variables
                try {
                  const evalFunc = new Function(...Object.keys(executionContext), ...Object.keys(variables), `return ${value};`);
                  variables[varName] = evalFunc(...Object.values(executionContext), ...Object.values(variables));
                } catch (e) {
                  variables[varName] = value;
                }
                continue;
              }
            }

            // Check if it's a print statement
            if (line.startsWith('print(')) {
              const content = line.match(/print\((.*)\)/)?.[1];
              if (content) {
                try {
                  // Split by comma but handle strings properly
                  const args = content.split(',').map(arg => arg.trim());
                  const evalFunc = new Function(...Object.keys(executionContext), ...Object.keys(variables),
                    `return [${args.join(', ')}];`);
                  const values = evalFunc(...Object.values(executionContext), ...Object.values(variables));
                  print(...values);
                } catch (e) {
                  errors.push(`Error in print: ${e}`);
                }
              }
              continue;
            }

            // Check if it's a function definition
            if (line.startsWith('def ')) {
              const funcLines = [line];
              let j = i + 1;
              while (j < lines.length && (lines[j].startsWith('    ') || lines[j].startsWith('\t') || lines[j].trim() === '')) {
                if (lines[j].trim()) funcLines.push(lines[j]);
                j++;
              }
              i = j - 1;

              const funcCode = funcLines.join('\n')
                .replace(/def\s+(\w+)\s*\((.*?)\):/g, 'function $1($2) {')
                .replace(/:\s*$/gm, ' {')
                .replace(/return\s+(.+)/g, 'return $1;')
                .replace(/\bTrue\b/g, 'true')
                .replace(/\bFalse\b/g, 'false')
                .replace(/\bNone\b/g, 'null')
                .replace(/if\s+(.+):/g, 'if ($1) {')
                .replace(/elif\s+(.+):/g, '} else if ($1) {')
                .replace(/else:/g, '} else {');

              const openBraces = (funcCode.match(/\{/g) || []).length;
              const closeBraces = (funcCode.match(/\}/g) || []).length;
              const finalFuncCode = funcCode + '\n' + '}'.repeat(Math.max(0, openBraces - closeBraces));

              const funcName = line.match(/def\s+(\w+)/)?.[1];
              if (funcName) {
                const evalFunc = new Function(...Object.keys(executionContext), ...Object.keys(variables), finalFuncCode + `; return ${funcName};`);
                functions[funcName] = evalFunc(...Object.values(executionContext), ...Object.values(variables));
              }
              continue;
            }

            // If it's the last line and it's just a variable/expression, display it
            if (i === lines.length - 1 && !line.includes('(') && !line.startsWith('print')) {
              try {
                const evalFunc = new Function(...Object.keys(executionContext), ...Object.keys(variables), `return ${line};`);
                const result = evalFunc(...Object.values(executionContext), ...Object.values(variables));
                if (result !== undefined) {
                  outputs.push(typeof result === 'object' ? JSON.stringify(result, null, 2) : String(result));
                }
              } catch (e) {
                // Ignore if not a valid expression
              }
            } else if (line.includes('(') && !line.startsWith('def ') && !line.startsWith('print(')) {
              try {
                const evalFunc = new Function(...Object.keys(executionContext), ...Object.keys(variables), `return ${line};`);
                const result = evalFunc(...Object.values(executionContext), ...Object.values(variables));
                if (result !== undefined && i === lines.length - 1) {
                  outputs.push(typeof result === 'object' ? JSON.stringify(result, null, 2) : String(result));
                }
              } catch (e) {
                // Ignore
              }
            }
          } catch (err) {
            // Continue to next line
          }
        }

        // Update shared notebook state with new variables and functions
        setNotebookVariables((prev: any) => ({ ...prev, ...variables }));
        setNotebookFunctions((prev: any) => ({ ...prev, ...functions }));

        const output = outputs.length > 0 ? outputs.join('\n') : '(No output)';
        const errorOutput = errors.length > 0 ? '\nErrors:\n' + errors.join('\n') : '';

        setCellOutputs((prev) => {
          const newOutputs = new Map(prev);
          newOutputs.set(cellId, {
            output: output + errorOutput,
            error: undefined,
          });
          return newOutputs;
        });

        toast.success('Code executed successfully');
      } catch (error: any) {
        const output = outputs.length > 0 ? outputs.join('\n') : '';
        setCellOutputs((prev) => {
          const newOutputs = new Map(prev);
          newOutputs.set(cellId, {
            output: output || undefined,
            error: `${error.name || 'Error'}: ${error.message || String(error)}`,
          });
          return newOutputs;
        });
        toast.error('Code execution failed');
      }
    } catch (error: any) {
      setCellOutputs((prev) => {
        const newOutputs = new Map(prev);
        newOutputs.set(cellId, {
          error: 'Failed to execute code: ' + (error.message || String(error)),
        });
        return newOutputs;
      });
      toast.error('Failed to execute code');
    } finally {
      setRunning(false);
      setRunningCell(null);
    }
  };

  const handleTestCell = async (cellId: string) => {
    if (!id) return;

    setTestingCell(cellId);
    setTesting(true);

    try {
      const response = await axiosInstance.post('/api/student/evaluate-cell', {
        assignment_id: id,
        cell_id: cellId,
        student_code: answers.get(cellId) || '',
      });

      const results = response.data.results || [];
      setTestResults(results);
      setShowResults(true);

      const totalScore = response.data.score || 0;
      const maxScore = response.data.max_score || 0;

      if (totalScore === maxScore) {
        toast.success(`✓ All tests passed! Score: ${totalScore}/${maxScore}`);
      } else if (totalScore > 0) {
        toast.info(`Partial score: ${totalScore}/${maxScore}`);
      } else {
        toast.error(`Tests failed: ${totalScore}/${maxScore}`);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to test code');
    } finally {
      setTesting(false);
      setTestingCell(null);
    }
  };

  const handleSubmitAll = () => {
    if (!id) return;

    // Convert answers map to array format
    const answerArray: CellAnswer[] = Array.from(answers.entries()).map(([cell_id, code]) => ({
      cell_id,
      code,
    }));

    submitMutation.mutate(
      {
        assignment_id: id,
        answers: answerArray,
      },
      {
        onSuccess: () => {
          toast.success('Assignment submitted successfully!');
          navigate('/student');
        },
      }
    );
  };

  if (isLoading) {
    return (
      <Content style={{ padding: '24px' }}>
        <Spin size="large" />
      </Content>
    );
  }

  if (!assignment) {
    return (
      <Content style={{ padding: '24px' }}>
        <Alert message="Assignment not found" type="error" />
      </Content>
    );
  }

  const dueDate = new Date(assignment.due_date);
  const isOverdue = dueDate < new Date();
  const totalPoints = assignment.questions?.reduce((sum, q) => sum + q.points, 0) || 0;

  const testResultColumns = [
    {
      title: 'Test Case',
      dataIndex: 'testcase_name',
      key: 'testcase_name',
    },
    {
      title: 'Status',
      dataIndex: 'passed',
      key: 'passed',
      render: (passed: boolean) => (
        <Tag color={passed ? 'success' : 'error'}>
          {passed ? 'PASSED' : 'FAILED'}
        </Tag>
      ),
    },
    {
      title: 'Score',
      key: 'score',
      render: (record: TestResult) => `${record.score}/${record.max_score}`,
    },
    {
      title: 'Feedback',
      dataIndex: 'feedback',
      key: 'feedback',
    },
  ];

  return (
    <Content style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Button onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        ← Back
      </Button>

      {/* Header Card */}
      <Card style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="small">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <Title level={2} style={{ margin: 0 }}>{assignment.title}</Title>
              <Space style={{ marginTop: 8 }}>
                <CalendarOutlined />
                <Text type={isOverdue ? 'danger' : 'secondary'}>
                  Due: {dueDate.toLocaleString()}
                </Text>
                {isOverdue && <Tag color="red">Overdue</Tag>}
              </Space>
            </div>
            <div style={{ textAlign: 'right' }}>
              <Text strong style={{ fontSize: 24, color: '#1890ff' }}>
                {totalPoints}
              </Text>
              <Text type="secondary"> points</Text>
            </div>
          </div>

          {assignment.description && (
            <>
              <Divider style={{ margin: '12px 0' }} />
              <div style={{
                padding: '12px',
                background: '#f5f5f5',
                borderRadius: '4px',
              }}>
                <ReactMarkdown>{assignment.description}</ReactMarkdown>
              </div>
            </>
          )}
        </Space>
      </Card>

      {/* Notebook-style Questions */}
      {!assignment.questions || assignment.questions.length === 0 ? (
        <Alert
          message="No questions available"
          description="This assignment doesn't have any questions yet."
          type="warning"
          showIcon
        />
      ) : (
        <>
          {assignment.questions.map((question) => (
            <QuestionCell
              key={question.cell_id}
              question={question}
              code={answers.get(question.cell_id) || ''}
              onCodeChange={(code) => handleCodeChange(question.cell_id, code)}
              onRun={() => handleRunCell(question.cell_id)}
              onTest={() => handleTestCell(question.cell_id)}
              running={running && runningCell === question.cell_id}
              testing={testing && testingCell === question.cell_id}
              output={cellOutputs.get(question.cell_id)?.output}
              error={cellOutputs.get(question.cell_id)?.error}
              onShiftEnter={() => focusNextCell(question.cell_id)}
            />
          ))}

          {/* Submit Button */}
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Button
                type="primary"
                size="large"
                icon={<SendOutlined />}
                onClick={handleSubmitAll}
                loading={submitMutation.isPending}
                disabled={answers.size === 0}
              >
                Submit All Answers
              </Button>
              <Paragraph type="secondary" style={{ marginTop: 8, marginBottom: 0 }}>
                Make sure to test your code before submitting!
              </Paragraph>
            </div>
          </Card>
        </>
      )}

      {/* Test Results Modal */}
      <Modal
        title="Test Results"
        open={showResults}
        onCancel={() => setShowResults(false)}
        footer={[
          <Button key="close" onClick={() => setShowResults(false)}>
            Close
          </Button>,
        ]}
        width={800}
      >
        <Table
          dataSource={testResults}
          columns={testResultColumns}
          rowKey="testcase_name"
          pagination={false}
        />
      </Modal>
    </Content>
  );
};

export default AssignmentNotebook;
