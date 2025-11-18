import React, { useState } from 'react';
import { Layout, Button, Space, Card, Typography, Divider, Row, Col } from 'antd';
import { PlusOutlined, PlayCircleOutlined, DeleteOutlined, SaveOutlined } from '@ant-design/icons';
import CodeEditor from '../components/CodeEditor';
import ReactMarkdown from 'react-markdown';

const { Content } = Layout;
const { Title } = Typography;

interface NotebookCell {
  id: string;
  type: 'markdown' | 'code';
  content: string;
  output?: string;
  error?: string;
}

const NotebookPage: React.FC = () => {
  const [cells, setCells] = useState<NotebookCell[]>([
    {
      id: '1',
      type: 'markdown',
      content: '# Python Notebook Environment\n\nThis is a demo of a Python notebook-like environment in React.\n\nYou can:\n- Write Markdown\n- Write Python code\n- Execute code (simulated)\n- Add/remove cells',
    },
    {
      id: '2',
      type: 'code',
      content: '# Example Python code\nimport numpy as np\nimport matplotlib.pyplot as plt\n\n# Create some data\nx = np.linspace(0, 10, 100)\ny = np.sin(x)\n\nprint("Hello from Python!")\nprint(f"Array shape: {x.shape}")',
      output: 'Hello from Python!\nArray shape: (100,)',
    },
  ]);

  const [editingCell, setEditingCell] = useState<string | null>(null);

  const addCell = (type: 'markdown' | 'code', afterId?: string) => {
    const newCell: NotebookCell = {
      id: Date.now().toString(),
      type,
      content: type === 'markdown' ? '# New Markdown Cell\n\nWrite your markdown here...' : '# Write your Python code here\n',
    };

    if (afterId) {
      const index = cells.findIndex((c) => c.id === afterId);
      const newCells = [...cells];
      newCells.splice(index + 1, 0, newCell);
      setCells(newCells);
    } else {
      setCells([...cells, newCell]);
    }
  };

  const updateCell = (id: string, content: string) => {
    setCells(cells.map((cell) => (cell.id === id ? { ...cell, content } : cell)));
  };

  const deleteCell = (id: string) => {
    if (cells.length > 1) {
      setCells(cells.filter((cell) => cell.id !== id));
    }
  };

  const runCell = (id: string) => {
    // Simulate code execution
    const cell = cells.find((c) => c.id === id);
    if (cell && cell.type === 'code') {
      // Simulate output
      const lines = cell.content.split('\n').filter((line) => line.trim().startsWith('print('));
      const output = lines.length > 0
        ? 'Simulated output:\n' + lines.map((line) => {
          const match = line.match(/print\((.*)\)/);
          return match ? match[1].replace(/['"]/g, '') : '';
        }).join('\n')
        : 'Code executed successfully! (No output)';

      setCells(
        cells.map((c) =>
          c.id === id ? { ...c, output, error: undefined } : c
        )
      );
    }
  };

  const changeCellType = (id: string, newType: 'markdown' | 'code') => {
    setCells(
      cells.map((cell) =>
        cell.id === id ? { ...cell, type: newType, output: undefined, error: undefined } : cell
      )
    );
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Layout.Header style={{ background: '#1890ff', padding: '0 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3} style={{ color: 'white', margin: '14px 0' }}>
            📓 Python Notebook - React Demo
          </Title>
          <Space>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              style={{ background: '#52c41a', borderColor: '#52c41a' }}
            >
              Save Notebook
            </Button>
            <Button type="default" style={{ background: 'white' }}>
              Download
            </Button>
          </Space>
        </div>
      </Layout.Header>

      <Content style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {cells.map((cell, index) => (
            <Card
              key={cell.id}
              style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
              bodyStyle={{ padding: 0 }}
            >
              {/* Cell Header */}
              <div
                style={{
                  padding: '8px 16px',
                  background: '#fafafa',
                  borderBottom: '1px solid #f0f0f0',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <Space>
                  <span style={{ color: '#999', fontFamily: 'monospace', fontSize: '12px' }}>
                    [{index + 1}]
                  </span>
                  <Button
                    size="small"
                    type={cell.type === 'code' ? 'primary' : 'default'}
                    onClick={() => changeCellType(cell.id, 'code')}
                  >
                    Code
                  </Button>
                  <Button
                    size="small"
                    type={cell.type === 'markdown' ? 'primary' : 'default'}
                    onClick={() => changeCellType(cell.id, 'markdown')}
                  >
                    Markdown
                  </Button>
                </Space>

                <Space>
                  {cell.type === 'code' && (
                    <Button
                      type="primary"
                      size="small"
                      icon={<PlayCircleOutlined />}
                      onClick={() => runCell(cell.id)}
                    >
                      Run
                    </Button>
                  )}
                  <Button
                    size="small"
                    onClick={() =>
                      setEditingCell(editingCell === cell.id ? null : cell.id)
                    }
                  >
                    {editingCell === cell.id ? 'View' : 'Edit'}
                  </Button>
                  <Button
                    size="small"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => deleteCell(cell.id)}
                    disabled={cells.length === 1}
                  >
                    Delete
                  </Button>
                </Space>
              </div>

              {/* Cell Content */}
              <div style={{ padding: '16px' }}>
                {editingCell === cell.id ? (
                  <CodeEditor
                    value={cell.content}
                    onChange={(value) => updateCell(cell.id, value || '')}
                    height="200px"
                    language={cell.type === 'code' ? 'python' : 'markdown'}
                  />
                ) : cell.type === 'markdown' ? (
                  <div
                    style={{
                      minHeight: '50px',
                      padding: '8px',
                      cursor: 'pointer',
                    }}
                    onClick={() => setEditingCell(cell.id)}
                  >
                    <ReactMarkdown>{cell.content}</ReactMarkdown>
                  </div>
                ) : (
                  <div
                    style={{
                      background: '#1e1e1e',
                      padding: '12px',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                    onClick={() => setEditingCell(cell.id)}
                  >
                    <pre
                      style={{
                        margin: 0,
                        color: '#d4d4d4',
                        fontFamily: 'monospace',
                        fontSize: '14px',
                      }}
                    >
                      {cell.content}
                    </pre>
                  </div>
                )}
              </div>

              {/* Cell Output */}
              {cell.output && (
                <>
                  <Divider style={{ margin: 0 }} />
                  <div
                    style={{
                      padding: '16px',
                      background: '#f9f9f9',
                      borderTop: '1px solid #e8e8e8',
                    }}
                  >
                    <div style={{ fontSize: '12px', color: '#999', marginBottom: '8px' }}>
                      Output:
                    </div>
                    <pre
                      style={{
                        margin: 0,
                        fontFamily: 'monospace',
                        fontSize: '13px',
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {cell.output}
                    </pre>
                  </div>
                </>
              )}

              {cell.error && (
                <>
                  <Divider style={{ margin: 0 }} />
                  <div
                    style={{
                      padding: '16px',
                      background: '#fff2f0',
                      borderTop: '1px solid #ffccc7',
                    }}
                  >
                    <div style={{ fontSize: '12px', color: '#cf1322', marginBottom: '8px' }}>
                      Error:
                    </div>
                    <pre
                      style={{
                        margin: 0,
                        color: '#cf1322',
                        fontFamily: 'monospace',
                        fontSize: '13px',
                      }}
                    >
                      {cell.error}
                    </pre>
                  </div>
                </>
              )}

              {/* Add Cell Buttons */}
              <div
                style={{
                  padding: '8px 16px',
                  background: '#fafafa',
                  borderTop: '1px solid #f0f0f0',
                  display: 'flex',
                  gap: '8px',
                  justifyContent: 'center',
                }}
              >
                <Button
                  size="small"
                  icon={<PlusOutlined />}
                  onClick={() => addCell('code', cell.id)}
                >
                  Code
                </Button>
                <Button
                  size="small"
                  icon={<PlusOutlined />}
                  onClick={() => addCell('markdown', cell.id)}
                >
                  Markdown
                </Button>
              </div>
            </Card>
          ))}

          {/* Add Cell at End */}
          <Card style={{ textAlign: 'center', background: '#fafafa' }}>
            <Space>
              <Button type="dashed" icon={<PlusOutlined />} onClick={() => addCell('code')}>
                Add Code Cell
              </Button>
              <Button
                type="dashed"
                icon={<PlusOutlined />}
                onClick={() => addCell('markdown')}
              >
                Add Markdown Cell
              </Button>
            </Space>
          </Card>
        </Space>

        {/* Info Footer */}
        <Card style={{ marginTop: '24px', background: '#e6f7ff', borderColor: '#91d5ff' }}>
          <Row gutter={16}>
            <Col span={8}>
              <div style={{ textAlign: 'center' }}>
                <Title level={4}>✨ Edit Cells</Title>
                <p style={{ fontSize: '12px', color: '#666' }}>
                  Click "Edit" to modify content
                </p>
              </div>
            </Col>
            <Col span={8}>
              <div style={{ textAlign: 'center' }}>
                <Title level={4}>▶️ Run Code</Title>
                <p style={{ fontSize: '12px', color: '#666' }}>
                  Execute Python code cells (simulated)
                </p>
              </div>
            </Col>
            <Col span={8}>
              <div style={{ textAlign: 'center' }}>
                <Title level={4}>➕ Add Cells</Title>
                <p style={{ fontSize: '12px', color: '#666' }}>
                  Insert code or markdown anywhere
                </p>
              </div>
            </Col>
          </Row>
        </Card>
      </Content>
    </Layout>
  );
};

export default NotebookPage;
