import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText, TrendingUp, Leaf, DollarSign, Clock, Upload } from 'lucide-react'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalShipments: 0,
    totalValue: 0,
    carbonSaved: 0,
    dutySaved: 0,
    timeSaved: 0
  })

  useEffect(() => {
    // Fetch user stats
    // For demo, using mock data
    setStats({
      totalShipments: 47,
      totalValue: 2450000,
      carbonSaved: 1847,
      dutySaved: 125000,
      timeSaved: 235
    })
  }, [])

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg shadow-xl p-8 mb-8 text-white">
        <h1 className="text-4xl font-bold mb-2">Welcome to ClearPath</h1>
        <p className="text-xl text-blue-100 mb-6">
          Your AI-powered customs compliance assistant
        </p>
        <Link
          to="/upload"
          className="inline-flex items-center gap-2 bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition"
        >
          <Upload className="w-5 h-5" />
          Start New Declaration
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        {/* Total Shipments */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <FileText className="w-8 h-8 text-blue-600" />
            <span className="text-sm text-gray-500">Total</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.totalShipments}</p>
          <p className="text-sm text-gray-600">Shipments</p>
        </div>

        {/* Total Value */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-8 h-8 text-green-600" />
            <span className="text-sm text-gray-500">Value</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            ${(stats.totalValue / 1000000).toFixed(1)}M
          </p>
          <p className="text-sm text-gray-600">Trade Volume</p>
        </div>

        {/* Carbon Saved */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <Leaf className="w-8 h-8 text-green-600" />
            <span className="text-sm text-gray-500">Impact</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.carbonSaved}</p>
          <p className="text-sm text-gray-600">kg CO₂ Saved</p>
        </div>

        {/* Duty Saved */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-8 h-8 text-yellow-600" />
            <span className="text-sm text-gray-500">Savings</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            ${(stats.dutySaved / 1000).toFixed(0)}K
          </p>
          <p className="text-sm text-gray-600">Duty Saved</p>
        </div>

        {/* Time Saved */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <Clock className="w-8 h-8 text-purple-600" />
            <span className="text-sm text-gray-500">Efficiency</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.timeSaved}</p>
          <p className="text-sm text-gray-600">Days Saved</p>
        </div>
      </div>

      {/* Recent Declarations */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Recent Declarations</h2>
        
        <div className="space-y-4">
          {/* Sample declaration */}
          <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-500 transition cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-gray-900">CLRP-20240327-A1B2</p>
                <p className="text-sm text-gray-600">Electronics - Mumbai to Dubai</p>
                <p className="text-xs text-gray-500 mt-1">Created 2 hours ago</p>
              </div>
              <div className="text-right">
                <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  Ready to Submit
                </span>
                <p className="text-sm text-gray-600 mt-2">$45,000 USD</p>
              </div>
            </div>
          </div>

          {/* Empty state */}
          {stats.totalShipments === 0 && (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">No declarations yet</p>
              <Link
                to="/upload"
                className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
              >
                <Upload className="w-5 h-5" />
                Create Your First Declaration
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
