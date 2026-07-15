// Envoltura de react-plotly.js usando la distribución mínima de Plotly.
import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-dist-min'

const Plot = createPlotlyComponent(Plotly)

// Tema claro común a todas las gráficas (coherente con el UX del tablero)
export const chartLayout = {
  paper_bgcolor: '#ffffff',
  plot_bgcolor: '#ffffff',
  font: { color: '#334155', family: 'Segoe UI, system-ui, sans-serif', size: 12 },
  margin: { t: 24, r: 20, b: 50, l: 55 },
  legend: { orientation: 'h', y: -0.2 },
  colorway: ['#2563eb', '#16a34a', '#f59e0b', '#8b5cf6', '#ef4444',
             '#0ea5e9', '#ec4899', '#14b8a6', '#a3a300'],
  xaxis: { gridcolor: '#eef2f7', zerolinecolor: '#e6eaf1' },
  yaxis: { gridcolor: '#eef2f7', zerolinecolor: '#e6eaf1' },
}

export default Plot
