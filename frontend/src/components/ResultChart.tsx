import React from 'react';
import { Card } from 'antd';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import { Submission } from '../api/submissionApi';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

interface ResultChartProps {
  submissions: Submission[];
  type?: 'bar' | 'pie';
}

const ResultChart: React.FC<ResultChartProps> = ({ submissions, type = 'bar' }) => {
  const gradedSubmissions = submissions.filter((s) => s.graded && s.score !== undefined);

  if (gradedSubmissions.length === 0) {
    return (
      <Card>
        <p style={{ textAlign: 'center', color: '#999' }}>
          No graded submissions available for visualization
        </p>
      </Card>
    );
  }

  // Score distribution data
  const scoreRanges = ['0-20', '21-40', '41-60', '61-80', '81-100'];
  const scoreCounts = [0, 0, 0, 0, 0];

  gradedSubmissions.forEach((sub) => {
    const percentage = ((sub.score || 0) / (sub.max_score || 100)) * 100;
    if (percentage <= 20) scoreCounts[0]++;
    else if (percentage <= 40) scoreCounts[1]++;
    else if (percentage <= 60) scoreCounts[2]++;
    else if (percentage <= 80) scoreCounts[3]++;
    else scoreCounts[4]++;
  });

  const barData = {
    labels: scoreRanges,
    datasets: [
      {
        label: 'Number of Students',
        data: scoreCounts,
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(255, 159, 64, 0.6)',
          'rgba(255, 205, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(54, 162, 235, 0.6)',
        ],
        borderColor: [
          'rgb(255, 99, 132)',
          'rgb(255, 159, 64)',
          'rgb(255, 205, 86)',
          'rgb(75, 192, 192)',
          'rgb(54, 162, 235)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const pieData = {
    labels: ['Failed (0-60)', 'Passed (61-80)', 'Excellent (81-100)'],
    datasets: [
      {
        data: [
          scoreCounts[0] + scoreCounts[1] + scoreCounts[2],
          scoreCounts[3],
          scoreCounts[4],
        ],
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(255, 205, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
        ],
        borderColor: [
          'rgb(255, 99, 132)',
          'rgb(255, 205, 86)',
          'rgb(75, 192, 192)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Grade Distribution',
      },
    },
  };

  return (
    <Card title="Analytics">
      {type === 'bar' ? (
        <Bar data={barData} options={options} />
      ) : (
        <Pie data={pieData} options={options} />
      )}
    </Card>
  );
};

export default ResultChart;
