import Head from 'next/head';

export default function Home() {
  return (
    <div className="bg-black text-white min-h-screen">
      <Head>
        <title>Crooks & Castles Command Center V2</title>
      </Head>

      <main className="p-8">
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-orange-500">👑 Crooks & Castles Command Center</h1>
          <nav className="flex space-x-4">
            <a href="#" className="text-lg font-semibold text-gray-300 hover:text-orange-500">Dashboard</a>
            <a href="#" className="text-lg font-semibold text-gray-300 hover:text-orange-500">Intelligence</a>
            <a href="#" className="text-lg font-semibold text-gray-300 hover:text-orange-500">Calendar</a>
            <a href="#" className="text-lg font-semibold text-gray-300 hover:text-orange-500">Agency</a>
          </nav>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {/* Stats Cards */}
          <div className="bg-gray-800 p-6 rounded-lg border border-orange-500">
            <h3 className="text-xl font-semibold mb-2">Total Brands</h3>
            <p className="text-4xl font-bold">16</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-lg border border-orange-500">
            <h3 className="text-xl font-semibold mb-2">Total Posts</h3>
            <p className="text-4xl font-bold">557</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-lg border border-orange-500">
            <h3 className="text-xl font-semibold mb-2">Positive Sentiment</h3>
            <p className="text-4xl font-bold">89.7%</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-lg border border-orange-500">
            <h3 className="text-xl font-semibold mb-2">C&C Rank</h3>
            <p className="text-4xl font-bold">#10</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-gray-900 p-6 rounded-lg">
            <h2 className="text-2xl font-bold mb-4 text-orange-500">Manual Data Ingest</h2>
            {/* Upload Component Goes Here */}
            <div className="bg-gray-800 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Upload JSON/CSV File</h3>
              <input type="file" className="w-full bg-gray-700 text-white p-2 rounded" />
              <button className="mt-4 w-full bg-orange-500 hover:bg-orange-600 text-white font-bold py-2 px-4 rounded">
                Upload & Process
              </button>
            </div>
          </div>
          <div className="bg-gray-900 p-6 rounded-lg">
            <h2 className="text-2xl font-bold mb-4 text-orange-500">System Health</h2>
            {/* System Health Component */}
            <div className="space-y-4">
              <p><strong>API Status:</strong> <span className="text-green-500">●</span> Online</p>
              <p><strong>Database:</strong> <span className="text-green-500">●</span> Connected</p>
              <p><strong>Last Update:</strong> Just now</p>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}

