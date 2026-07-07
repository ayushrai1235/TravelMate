'use client'

import { useState } from 'react'
import { Search } from 'lucide-react'

const stations = [
  { code: 'NDLS', name: 'New Delhi', city: 'New Delhi' },
  { code: 'NZM', name: 'Hazrat Nizamuddin', city: 'New Delhi' },
  { code: 'DSA', name: 'Delhi Sarai Rohilla', city: 'New Delhi' },
  { code: 'DLI', name: 'Delhi Junction', city: 'New Delhi' },
  { code: 'ANVT', name: 'Anand Vihar Terminal', city: 'New Delhi' },
  { code: 'HWH', name: 'Howrah Junction', city: 'Kolkata' },
  { code: 'KOAA', name: 'Kolkata', city: 'Kolkata' },
  { code: 'SDAH', name: 'Sealdah', city: 'Kolkata' },
  { code: 'MMCT', name: 'Mumbai Central', city: 'Mumbai' },
  { code: 'CSTM', name: 'Chhatrapati Shivaji Maharaj Terminus', city: 'Mumbai' },
  { code: 'LTT', name: 'Lokmanya Tilak Terminus', city: 'Mumbai' },
  { code: 'BCT', name: 'Mumbai Central (old)', city: 'Mumbai' },
  { code: 'BVI', name: 'Borivali', city: 'Mumbai' },
  { code: 'BDTS', name: 'Bandra Terminus', city: 'Mumbai' },
  { code: 'SBC', name: 'KSR Bengaluru City Junction', city: 'Bengaluru' },
  { code: 'YPR', name: 'Yesvantpur Junction', city: 'Bengaluru' },
  { code: 'KJM', name: 'Krishnarajapuram', city: 'Bengaluru' },
  { code: 'BNC', name: 'Bangalore Cantonment', city: 'Bengaluru' },
  { code: 'MAS', name: 'Chennai Central', city: 'Chennai' },
  { code: 'MS', name: 'Chennai Egmore', city: 'Chennai' },
  { code: 'TBM', name: 'Tambaram', city: 'Chennai' },
  { code: 'AJJ', name: 'Arakkonam', city: 'Chennai' },
  { code: 'HYB', name: 'Hyderabad Deccan', city: 'Hyderabad' },
  { code: 'SC', name: 'Secunderabad Junction', city: 'Hyderabad' },
  { code: 'KCG', name: 'Kacheguda', city: 'Hyderabad' },
  { code: 'BZA', name: 'Vijayawada Junction', city: 'Vijayawada' },
  { code: 'VZM', name: 'Vizag', city: 'Visakhapatnam' },
  { code: 'VSKP', name: 'Visakhapatnam', city: 'Visakhapatnam' },
  { code: 'TPY', name: 'Tirupati', city: 'Tirupati' },
  { code: 'RU', name: 'Renigunta', city: 'Tirupati' },
  { code: 'MDU', name: 'Madurai Junction', city: 'Madurai' },
  { code: 'CBE', name: 'Coimbatore Junction', city: 'Coimbatore' },
  { code: 'ERS', name: 'Ernakulam Junction', city: 'Kochi' },
  { code: 'ERN', name: 'Ernakulam Town', city: 'Kochi' },
  { code: 'KTYM', name: 'Kottayam', city: 'Kottayam' },
  { code: 'TRV', name: 'Trivandrum Central', city: 'Thiruvananthapuram' },
  { code: 'PGW', name: 'Palghat', city: 'Palakkad' },
  { code: 'SRR', name: 'Shoranur Junction', city: 'Shoranur' },
  { code: 'LKO', name: 'Lucknow Charbagh', city: 'Lucknow' },
  { code: 'GNCT', name: 'Gomti Nagar', city: 'Lucknow' },
  { code: 'Kanpur', name: 'Kanpur Central', city: 'Kanpur' },
  { code: 'CNB', name: 'Kanpur Central', city: 'Kanpur' },
  { code: 'JHS', name: 'Jhansi Junction', city: 'Jhansi' },
  { code: 'JBP', name: 'Jabalpur', city: 'Jabalpur' },
  { code: 'BPL', name: 'Bhopal', city: 'Bhopal' },
  { code: 'BPL', name: 'Bhopal Junction', city: 'Bhopal' },
  { code: 'ET', name: 'Ujjain Junction', city: 'Ujjain' },
  { code: 'INDB', name: 'Indore Junction', city: 'Indore' },
  { code: 'RTM', name: 'Ratlam Junction', city: 'Ratlam' },
  { code: 'AGC', name: 'Agra Cantt', city: 'Agra' },
  { code: 'AF', name: 'Agra Fort', city: 'Agra' },
  { code: 'GWL', name: 'Gwalior', city: 'Gwalior' },
  { code: 'JHR', name: 'Jhansi', city: 'Jhansi' },
  { code: 'PRYJ', name: 'Prayagraj Junction', city: 'Prayagraj' },
  { code: 'VGLJ', name: 'Jhansi', city: 'Jhansi' },
  { code: 'BSB', name: 'Varanasi Junction', city: 'Varanasi' },
  { code: 'MUV', name: 'Manduadih', city: 'Varanasi' },
  { code: 'DURG', name: 'Durg', city: 'Durg' },
  { code: 'RIG', name: 'Raipur', city: 'Raipur' },
  { code: 'SRC', name: 'Santragachi', city: 'Kolkata' },
  { code: 'BWN', name: 'Barddhaman', city: 'Bardhaman' },
  { code: 'NJP', name: 'New Jalpaiguri', city: 'Siliguri' },
  { code: 'DBRT', name: 'Dibrugarh', city: 'Dibrugarh' },
  { code: 'GHY', name: 'Guwahati', city: 'Guwahati' },
  { code: 'SCL', name: 'Silchar', city: 'Silchar' },
  { code: 'AGTL', name: 'Guwahati', city: 'Guwahati' },
  { code: 'PUNE', name: 'Pune Junction', city: 'Pune' },
  { code: 'KYN', name: 'Kalyan Junction', city: 'Kalyan' },
  { code: 'KOP', name: 'Kolhapur', city: 'Kolhapur' },
  { code: 'NGP', name: 'Nagpur', city: 'Nagpur' },
  { code: 'AMI', name: 'Amravati', city: 'Amravati' },
  { code: 'WL', name: 'Wardha', city: 'Wardha' },
  { code: 'CHD', name: 'Chandigarh', city: 'Chandigarh' },
  { code: 'UMB', name: 'Ambala Cantt', city: 'Ambala' },
  { code: 'KKDE', name: 'Kurukshetra', city: 'Kurukshetra' },
  { code: 'SVDK', name: 'Shri Mata Vaishno Devi Katra', city: 'Katra' },
  { code: 'UDR', name: 'Udhampur', city: 'Udhampur' },
  { code: 'LEH', name: 'Leh', city: 'Leh' },
  { code: 'GAYA', name: 'Gaya Junction', city: 'Gaya' },
  { code: 'DHN', name: 'Dhanbad', city: 'Dhanbad' },
  { code: 'ASN', name: 'Asansol', city: 'Asansol' },
  { code: 'BHP', name: 'Bhagalpur', city: 'Bhagalpur' },
  { code: 'MFP', name: 'Muzaffarpur Junction', city: 'Muzaffarpur' },
  { code: 'CPJ', name: 'Chhapra', city: 'Chhapra' },
  { code: 'SPJ', name: 'Samastipur', city: 'Samastipur' },
  { code: 'JBN', name: 'Jogbani', city: 'Jogbani' },
  { code: 'BOE', name: 'Birni', city: 'Birni' },
  { code: 'RJPB', name: 'Patna Junction', city: 'Patna' },
  { code: 'PNBE', name: 'Patna Junction', city: 'Patna' },
  { code: 'DNR', name: 'Dumraon', city: 'Dumraon' },
  { code: 'GKP', name: 'Gorakhpur', city: 'Gorakhpur' },
  { code: 'DEE', name: 'Delhi Sarai Rohilla', city: 'Delhi' },
  { code: 'FZR', name: 'Firozpur Cantt', city: 'Firozpur' },
  { code: 'JUC', name: 'Jalandhar City', city: 'Jalandhar' },
  { code: 'LDH', name: 'Ludhiana', city: 'Ludhiana' },
  { code: 'ABS', name: 'Ambala Sadar', city: 'Ambala' },
  { code: 'KOT', name: 'Kotli Kalan', city: 'Kotli Kalan' },
  { code: 'SRE', name: 'Saharanpur', city: 'Saharanpur' },
  { code: 'MB', name: 'Moradabad', city: 'Moradabad' },
  { code: 'BE', name: 'Bareilly', city: 'Bareilly' },
  { code: 'TPU', name: 'Tanakpur', city: 'Tanakpur' },
  { code: 'KFF', name: 'Kathgodam', city: 'Kathgodam' },
  { code: 'HRI', name: 'Haridwar', city: 'Haridwar' },
  { code: 'HW', name: 'Haridwar Junction', city: 'Haridwar' },
  { code: 'DEHRADUN', name: 'Dehradun', city: 'Dehradun' },
  { code: 'DDN', name: 'Dehradun', city: 'Dehradun' },
  { code: 'JAT', name: 'Jammu Tawi', city: 'Jammu' },
  { code: 'SMPB', name: 'Shri Mata Vaishno Devi Katra', city: 'Katra' },
  { code: 'BRC', name: 'Ahmedabad Junction', city: 'Ahmedabad' },
  { code: 'ADI', name: 'Ahmedabad Junction', city: 'Ahmedabad' },
  { code: 'RJT', name: 'Rajkot Junction', city: 'Rajkot' },
  { code: 'GIMB', name: 'Gandhidham', city: 'Gandhidham' },
  { code: 'Bhuj', name: 'Bhuj', city: 'Bhuj' },
  { code: 'ABR', name: 'Abu Road', city: 'Abu Road' },
  { code: 'JP', name: 'Jaipur Junction', city: 'Jaipur' },
  { code: 'AII', name: 'Ajmer Junction', city: 'Ajmer' },
  { code: 'COR', name: 'Coimbatore', city: 'Coimbatore' },
  { code: 'TPJ', name: 'Tiruchirappalli', city: 'Trichy' },
  { code: 'SA', name: 'Salem Junction', city: 'Salem' },
  { code: 'DMV', name: 'Dhamtari', city: 'Dhamtari' },
  { code: 'KUR', name: 'Khurda Road', city: 'Bhubaneswar' },
  { code: 'BBS', name: 'Bhubaneswar', city: 'Bhubaneswar' },
  { code: 'BHC', name: 'Bhadrak', city: 'Bhadrak' },
  { code: 'BAM', name: 'Brahmapur', city: 'Brahmapur' },
  { code: 'BAM', name: 'Brahmapur', city: 'Brahmapur' },
  { code: 'CTC', name: 'Cuttack', city: 'Cuttack' },
  { code: 'BHC', name: 'Bhadrak', city: 'Bhadrak' },
  { code: 'NRH', name: 'Narasaraopet', city: 'Narasaraopet' },
  { code: 'OGL', name: 'Ongole', city: 'Ongole' },
  { code: 'NLR', name: 'Nidadavole', city: 'Nidadavole' },
  { code: 'TPTM', name: 'Tirupati', city: 'Tirupati' },
  { code: 'GDR', name: 'Gudur', city: 'Gudur' },
  { code: 'KPD', name: 'Katpadi', city: 'Vellore' },
  { code: 'VRI', name: 'Vellore', city: 'Vellore' },
  { code: 'VRI', name: 'Vellore Cantonment', city: 'Vellore' },
  { code: 'KLN', name: 'Kallakudi', city: 'Kallakudi' },
  { code: 'KQN', name: 'Kanniyakumari', city: 'Kanyakumari' },
  { code: 'NME', name: 'Nagercoil', city: 'Nagercoil' },
  { code: 'TVC', name: 'Thiruvananthapuram Central', city: 'Thiruvananthapuram' },
  { code: 'QLN', name: 'Kollam', city: 'Kollam' },
  { code: 'AWY', name: 'Alappuzha', city: 'Alappuzha' },
  { code: 'PGTN', name: 'Palghat Town', city: 'Palghat' },
  { code: 'CNGR', name: 'Chengannur', city: 'Chengannur' },
  { code: 'KLLM', name: 'Kallai', city: 'Kallai' },
  { code: 'PER', name: 'Perinthalmanna', city: 'Perinthalmanna' },
  { code: 'TCR', name: 'Thirakkara', city: 'Thirakkara' },
  { code: 'MALM', name: 'Malappuram', city: 'Malappuram' },
  { code: 'PNBE', name: 'Patna Junction', city: 'Patna' },
  { code: 'GAYA', name: 'Gaya Junction', city: 'Gaya' },
  { code: 'DHN', name: 'Dhanbad Junction', city: 'Dhanbad' },
  { code: 'ASN', name: 'Asansol Junction', city: 'Asansol' },
  { code: 'BHP', name: 'Bhagalpur', city: 'Bhagalpur' },
  { code: 'MFP', name: 'Muzaffarpur Junction', city: 'Muzaffarpur' },
  { code: 'CPJ', name: 'Chhapra', city: 'Chhapra' },
  { code: 'SPJ', name: 'Samastipur Junction', city: 'Samastipur' },
  { code: 'JBN', name: 'Jogbani', city: 'Jogbani' },
  { code: 'BOE', name: 'Birni', city: 'Birni' },
  { code: 'RJPB', name: 'Patna Sahib', city: 'Patna' },
  { code: 'GKP', name: 'Gorakhpur Junction', city: 'Gorakhpur' },
  { code: 'DEE', name: 'Delhi Sarai Rohilla', city: 'Delhi' },
  { code: 'FZR', name: 'Firozpur Cantt', city: 'Firozpur' },
  { code: 'JUC', name: 'Jalandhar City', city: 'Jalandhar' },
  { code: 'LDH', name: 'Ludhiana Junction', city: 'Ludhiana' },
  { code: 'ABS', name: 'Ambala Sadar', city: 'Ambala' },
  { code: 'KOT', name: 'Kotli Kalan', city: 'Kotli Kalan' },
  { code: 'SRE', name: 'Saharanpur', city: 'Saharanpur' },
  { code: 'MB', name: 'Moradabad', city: 'Moradabad' },
  { code: 'BE', name: 'Bareilly', city: 'Bareilly' },
  { code: 'TPU', name: 'Tanakpur', city: 'Tanakpur' },
  { code: 'KFF', name: 'Kathgodam', city: 'Kathgodam' },
  { code: 'HRI', name: 'Haridwar', city: 'Haridwar' },
  { code: 'HW', name: 'Haridwar Junction', city: 'Haridwar' },
  { code: 'DDN', name: 'Dehradun', city: 'Dehradun' },
  { code: 'JAT', name: 'Jammu Tawi', city: 'Jammu' },
  { code: 'SMPB', name: 'Shri Mata Vaishno Devi Katra', city: 'Katra' },
  { code: 'BRC', name: 'Ahmedabad Junction', city: 'Ahmedabad' },
  { code: 'ADI', name: 'Ahmedabad Junction', city: 'Ahmedabad' },
  { code: 'RJT', name: 'Rajkot Junction', city: 'Rajkot' },
  { code: 'GIMB', name: 'Gandhidham', city: 'Gandhidham' },
  { code: 'Bhuj', name: 'Bhuj', city: 'Bhuj' },
  { code: 'ABR', name: 'Abu Road', city: 'Abu Road' },
  { code: 'JP', name: 'Jaipur Junction', city: 'Jaipur' },
  { code: 'AII', name: 'Ajmer Junction', city: 'Ajmer' },
  { code: 'COR', name: 'Coimbatore', city: 'Coimbatore' },
  { code: 'TPJ', name: 'Tiruchirappalli', city: 'Trichy' },
  { code: 'SA', name: 'Salem Junction', city: 'Salem' },
  { code: 'DMV', name: 'Dhamtari', city: 'Dhamtari' },
  { code: 'KUR', name: 'Khurda Road', city: 'Bhubaneswar' },
  { code: 'BBS', name: 'Bhubaneswar', city: 'Bhubaneswar' },
  { code: 'BHC', name: 'Bhadrak', city: 'Bhadrak' },
  { code: 'BAM', name: 'Brahmapur', city: 'Brahmapur' },
  { code: 'CTC', name: 'Cuttack', city: 'Cuttack' },
  { code: 'NRH', name: 'Narasaraopet', city: 'Narasaraopet' },
  { code: 'OGL', name: 'Ongole', city: 'Ongole' },
  { code: 'NLR', name: 'Nidadavole', city: 'Nidadavole' },
  { code: 'TPTM', name: 'Tirupati', city: 'Tirupati' },
  { code: 'GDR', name: 'Gudur', city: 'Gudur' },
  { code: 'KPD', name: 'Katpadi', city: 'Vellore' },
  { code: 'VRI', name: 'Vellore Cantonment', city: 'Vellore' },
  { code: 'KLN', name: 'Kallakudi', city: 'Kallakudi' },
  { code: 'KQN', name: 'Kanniyakumari', city: 'Kanyakumari' },
  { code: 'NME', name: 'Nagercoil', city: 'Nagercoil' },
  { code: 'TVC', name: 'Thiruvananthapuram Central', city: 'Thiruvananthapuram' },
  { code: 'QLN', name: 'Kollam', city: 'Kollam' },
  { code: 'AWY', name: 'Alappuzha', city: 'Alappuzha' },
  { code: 'PGTN', name: 'Palghat Town', city: 'Palghat' },
  { code: 'CNGR', name: 'Chengannur', city: 'Chengannur' },
  { code: 'KLLM', name: 'Kallai', city: 'Kallai' },
  { code: 'PER', name: 'Perinthalmanna', city: 'Perinthalmanna' },
  { code: 'TCR', name: 'Thirakkara', city: 'Thirakkara' },
  { code: 'MALM', name: 'Malappuram', city: 'Malappuram' },
]

export default function StationsPage() {
  const [search, setSearch] = useState('')
  const [cityFilter, setCityFilter] = useState('All')

  const cities = ['All', ...new Set(stations.map((s) => s.city))]

  const filtered = stations.filter((station) => {
    const matchesSearch =
      search === '' ||
      station.code.toLowerCase().includes(search.toLowerCase()) ||
      station.name.toLowerCase().includes(search.toLowerCase()) ||
      station.city.toLowerCase().includes(search.toLowerCase())
    const matchesCity = cityFilter === 'All' || station.city === cityFilter
    return matchesSearch && matchesCity
  })

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-slate-950 dark:text-white">Indian Railways Station Codes</h1>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            Search and copy station codes for trip planning. These are the official Indian Railways station codes.
          </p>
        </div>

        <div className="mb-6 flex flex-col gap-4 sm:flex-row">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
            <input
              type="text"
              placeholder="Search by station name, code, or city..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-10 w-full rounded-md border border-slate-300 bg-white pl-10 pr-3 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-950/10 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
            />
          </div>
          <select
            value={cityFilter}
            onChange={(e) => setCityFilter(e.target.value)}
            className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-950/10 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
          >
            {cities.map((city) => (
              <option key={city} value={city}>
                {city}
              </option>
            ))}
          </select>
        </div>

        <p className="mb-4 text-xs text-slate-500 dark:text-slate-400">
          {filtered.length} station{filtered.length !== 1 ? 's' : ''} found
        </p>

        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-900">
                  <th className="px-4 py-3 text-left font-medium text-slate-700 dark:text-slate-300">Code</th>
                  <th className="px-4 py-3 text-left font-medium text-slate-700 dark:text-slate-300">Station Name</th>
                  <th className="px-4 py-3 text-left font-medium text-slate-700 dark:text-slate-300">City</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((station) => (
                  <tr
                    key={station.code}
                    className="border-b border-slate-100 transition-colors hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-900"
                  >
                    <td className="px-4 py-3">
                      <button
                        type="button"
                        className="rounded bg-slate-100 px-2 py-1 font-mono text-xs font-bold text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                        onClick={() => {
                          navigator.clipboard.writeText(station.code)
                        }}
                        title="Click to copy"
                      >
                        {station.code}
                      </button>
                    </td>
                    <td className="px-4 py-3 text-slate-900 dark:text-white">{station.name}</td>
                    <td className="px-4 py-3 text-slate-500 dark:text-slate-400">{station.city}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filtered.length === 0 && (
            <div className="py-12 text-center text-sm text-slate-500 dark:text-slate-400">
              No stations found matching your search.
            </div>
          )}
        </div>

        <div className="mt-8 rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-900/60 dark:bg-amber-950/30">
          <h3 className="text-sm font-semibold text-amber-900 dark:text-amber-200">How to use station codes</h3>
          <ol className="mt-2 list-inside list-decimal space-y-1 text-sm text-amber-800 dark:text-amber-300">
            <li>Search for your departure city and note the station code</li>
            <li>Search for your destination city and note the station code</li>
            <li>Enter the station names (not codes) in the Trip Planner form</li>
            <li>The backend will resolve station names to codes automatically</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
