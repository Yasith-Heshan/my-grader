import React from 'react';
import Editor from '@monaco-editor/react';
import { Card } from 'antd';

interface CodeEditorProps {
  value: string;
  onChange: (value: string | undefined) => void;
  height?: string;
  readOnly?: boolean;
  language?: string;
  onCtrlEnter?: () => void;
  onShiftEnter?: () => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  height = '400px',
  readOnly = false,
  language = 'python',
  onCtrlEnter,
  onShiftEnter,
}) => {
  const handleEditorDidMount = (editor: any, monaco: any) => {
    // Add keyboard shortcuts
    if (onCtrlEnter) {
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
        onCtrlEnter();
      });
    }
    
    if (onShiftEnter) {
      editor.addCommand(monaco.KeyMod.Shift | monaco.KeyCode.Enter, () => {
        onShiftEnter();
      });
    }
  };

  return (
    <Card>
      <Editor
        height={height}
        defaultLanguage={language}
        language={language}
        value={value}
        onChange={onChange}
        onMount={handleEditorDidMount}
        theme="vs-dark"
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 4,
          wordWrap: 'on',
        }}
      />
    </Card>
  );
};

export default CodeEditor;
