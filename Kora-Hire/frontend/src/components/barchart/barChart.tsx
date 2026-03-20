import React, { useEffect, useRef } from "react";
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  ChartConfiguration,
} from "chart.js";
import { ProfileCategoryScore } from "../../types/applicantProfile";
import "./barChart.css";

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip);

interface BarChartProps {
  canvasId: string;
  data: ProfileCategoryScore[];
}

const BarChart: React.FC<BarChartProps> = ({ canvasId, data }) => {
  const chartRef = useRef<HTMLCanvasElement | null>(null);
  const barChartRef = useRef<Chart | null>(null);

  useEffect(() => {
    if (!data || data.length === 0) return;

    const labels = data.map((item) => item.category);
    const scores = data.map((item) => item.category_score);

    if (barChartRef.current) {
      barChartRef.current.destroy();
    }

    if (!chartRef.current) return;
    const ctx = chartRef.current.getContext("2d");
    if (!ctx) return;

    const config: ChartConfiguration = {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Candidate Attribute Scores",
            data: scores,
            backgroundColor: "rgba(9, 134, 102, 0.6)",
            borderColor: "#098666",
            borderWidth: 1,
            borderRadius: 10,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        indexAxis: "y",
        scales: {
          x: {
            beginAtZero: true,
            max: 10,
            ticks: { stepSize: 1, font: { family: "Lexend" } },
            grid: { display: false },
          },
          y: {
            ticks: { font: { family: "Lexend" } },
            grid: { display: false },
          },
        },
        plugins: {
          legend: { labels: { font: { family: "Lexend" } } },
        },
      },
    };

    barChartRef.current = new Chart(ctx, config);

    return () => {
      if (barChartRef.current) {
        barChartRef.current.destroy();
      }
    };
  }, [data]);

  return (
    <div className="bar-chart-container">
      <canvas id={canvasId} ref={chartRef}></canvas>
    </div>
  );
};

export default BarChart;