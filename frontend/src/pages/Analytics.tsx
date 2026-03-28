import { useState } from 'react'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, Leaf, DollarSign, Globe } from 'lucide-react'

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('30d')

  // Mock data - replace with API calls
  const monthlyData = [
    { month: 'Oct', shipments: 12, value: 450000, carbon: 340 },
    { month: 'Nov', shipments: 18, value: 680000, carbon: 520 },
    { month: 'Dec', shipments: 25, value: 920000, carbon: 710 },
    { month: 'Jan', shipments: 32, value: 1200000, carbon: 890 },
    { month: 'Feb', shipments: 41, value: 1580000, carbon: 1150 },
    { month: 'Mar', shipments: 47, value: 2450000, carbon: 1847 }
  ]

  const corridorData = [
    { name: 'India-UAE', value: 65, color: '#3B82F6' },
    { name: 'India-Singapore', value: 20, color: '#10B981' },
    { name: 'India-UK', value: 10, color: '#F59E0B' },
    { name: 'India-USA', value: 5, color: '#8B5CF6' }
  ]

  const hsCodeData = [
    { code: '8471.30', description: 'Laptops', count: 15 },
    { code: '6109.10', description: 'T-Shirts', count: 12 },
    { code: '8517.12', description: 'Smartphones', count: 10 },
    { code: '7113.11', description: 'Jewelry', count: 8 },
    { code: '3004.90', description: 'Medicines', count: 6 }
  ]

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analytics & Insights</h1>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
          <option value="90d">Last 90 Days</option>
          <option value="1y">Last Year</option>
        </select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            <h3 className="font-semibold text-gray-700">Total Value</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900">$2.45M</p>
          <p className="text-sm text-green-600 mt-1">↑ 24% vs last month</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <Leaf className="w-6 h-6 text-green-600" />
            <h3 className="font-semibold text-gray-700">CO₂ Saved</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900">1.8 tons</p>
          <p className="text-sm text-gray-600 mt-1">By faster clearance</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <DollarSign className="w-6 h-6 text-yellow-600" />
            <h3 className="font-semibold text-gray-700">Duty Saved</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900">$125K</p>
          <p className="text-sm text-gray-600 mt-1">Via FTA optimization</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <Globe className="w-6 h-6 text-purple-600" />
            <h3 className="font-semibold text-gray-700">Corridors</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900">4</p>
          <p className="text-sm text-gray-600 mt-1">Active trade routes</p>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Shipment Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Shipment Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="shipments" stroke="#3B82F6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Trade Value */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Trade Value ($)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Carbon Emissions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Carbon Footprint (kg CO₂)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="carbon" stroke="#10B981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Trade Corridors */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Trade Corridors</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={corridorData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {corridorData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top HS Codes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Top HS Codes</h3>
        <div className="space-y-3">
          {hsCodeData.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-mono font-semibold text-gray-900">{item.code}</p>
                <p className="text-sm text-gray-600">{item.description}</p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-gray-900">{item.count}</p>
                <p className="text-xs text-gray-500">shipments</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
