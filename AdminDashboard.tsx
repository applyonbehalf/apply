// AdminDashboard.tsx - Fixed version for your frontend
import { useState, useEffect } from 'react';

interface JobCategory {
  id: string;
  category_name: string;
  description: string;
}

interface JobUrl {
  id: string;
  category_id: string;
  category_name: string;
  job_url: string;
  status: string;
  created_at: string;
}

interface AdminStats {
  total_users: number;
  total_categories: number;
  total_job_urls: number;
  active_applications: number;
  completed_applications: number;
  failed_applications: number;
  pending_captchas: number;
}

const AdminDashboard = () => {
  const [categories, setCategories] = useState<JobCategory[]>([]);
  const [jobUrls, setJobUrls] = useState<JobUrl[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [newUrls, setNewUrls] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // Use your deployed backend URL or localhost for testing
  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8002';

  // Get auth token from localStorage
  const getAuthHeaders = () => {
    const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  };

  // Load initial data
  useEffect(() => {
    loadCategories();
    loadJobUrls();
    loadStats();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/categories`, {
        headers: getAuthHeaders()
      });
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      } else {
        console.error('Failed to load categories:', response.status);
      }
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadJobUrls = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/job-urls`, {
        headers: getAuthHeaders()
      });
      if (response.ok) {
        const data = await response.json();
        setJobUrls(data);
      } else {
        console.error('Failed to load job URLs:', response.status);
      }
    } catch (error) {
      console.error('Error loading job URLs:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/stats`, {
        headers: getAuthHeaders()
      });
      if (response.ok) {
        const result = await response.json();
        setStats(result.data);
      } else {
        console.error('Failed to load stats:', response.status);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleAddUrls = async () => {
    if (!selectedCategory || !newUrls.trim()) {
      alert('Please select a category and enter URLs');
      return;
    }

    setIsLoading(true);
    try {
      const urls = newUrls.split('\n').filter(url => url.trim());
      
      const response = await fetch(`${API_BASE}/api/admin/job-urls`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          category_id: selectedCategory,
          urls: urls
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Success! Added ${urls.length} URLs and created ${result.data.applications_created} applications`);
        setNewUrls('');
        loadJobUrls();
        loadStats();
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || 'Failed to add URLs'}`);
      }
    } catch (error) {
      console.error('Error adding URLs:', error);
      alert('Error adding URLs. Check console for details.');
    }
    setIsLoading(false);
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', padding: '24px' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '30px', fontWeight: 'bold', color: '#111827', margin: 0 }}>
            Admin Dashboard
          </h1>
          <p style={{ color: '#6b7280', margin: '8px 0 0 0' }}>
            Manage job categories and URLs for all users
          </p>
        </div>

        {/* Statistics Cards */}
        {stats && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '24px', 
            marginBottom: '32px' 
          }}>
            <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', margin: '0 0 8px 0' }}>Total Users</h3>
              <p style={{ fontSize: '30px', fontWeight: 'bold', color: '#2563eb', margin: 0 }}>{stats.total_users}</p>
            </div>
            <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', margin: '0 0 8px 0' }}>Job Categories</h3>
              <p style={{ fontSize: '30px', fontWeight: 'bold', color: '#16a34a', margin: 0 }}>{stats.total_categories}</p>
            </div>
            <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', margin: '0 0 8px 0' }}>Total Job URLs</h3>
              <p style={{ fontSize: '30px', fontWeight: 'bold', color: '#9333ea', margin: 0 }}>{stats.total_job_urls}</p>
            </div>
            <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', margin: '0 0 8px 0' }}>Pending CAPTCHAs</h3>
              <p style={{ fontSize: '30px', fontWeight: 'bold', color: '#dc2626', margin: 0 }}>{stats.pending_captchas}</p>
              {stats.pending_captchas > 0 && (
                <p style={{ fontSize: '14px', color: '#dc2626', margin: '4px 0 0 0' }}>Needs your attention!</p>
              )}
            </div>
          </div>
        )}

        {/* Add Job URLs Section */}
        <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '24px', marginBottom: '32px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', margin: '0 0 16px 0' }}>Add Job URLs</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
            {/* Category Selection */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
                Job Category
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                style={{ 
                  width: '100%', 
                  padding: '12px', 
                  border: '1px solid #d1d5db', 
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              >
                <option value="">Select a category</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.category_name}
                  </option>
                ))}
              </select>
            </div>

            {/* URL Input */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
                Job URLs (one per line)
              </label>
              <textarea
                value={newUrls}
                onChange={(e) => setNewUrls(e.target.value)}
                placeholder={`https://company1.com/job1\nhttps://company2.com/job2\nhttps://company3.com/job3`}
                rows={6}
                style={{ 
                  width: '100%', 
                  padding: '12px', 
                  border: '1px solid #d1d5db', 
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontFamily: 'monospace'
                }}
              />
              <p style={{ fontSize: '12px', color: '#6b7280', margin: '4px 0 0 0' }}>
                {newUrls.split('\n').filter(url => url.trim()).length} URLs entered
              </p>
            </div>
          </div>

          <div style={{ marginTop: '24px' }}>
            <button
              onClick={handleAddUrls}
              disabled={isLoading || !selectedCategory || !newUrls.trim()}
              style={{ 
                backgroundColor: isLoading || !selectedCategory || !newUrls.trim() ? '#9ca3af' : '#2563eb',
                color: 'white', 
                padding: '12px 24px', 
                borderRadius: '6px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '500',
                cursor: isLoading || !selectedCategory || !newUrls.trim() ? 'not-allowed' : 'pointer'
              }}
            >
              {isLoading ? 'Adding URLs...' : 'Add URLs & Create Applications'}
            </button>
          </div>

          {selectedCategory && (
            <div style={{ 
              marginTop: '16px', 
              padding: '16px', 
              backgroundColor: '#eff6ff', 
              borderRadius: '6px',
              border: '1px solid #bfdbfe'
            }}>
              <h4 style={{ fontWeight: '500', color: '#1e40af', margin: '0 0 8px 0' }}>What happens when you add URLs:</h4>
              <ul style={{ color: '#1e40af', fontSize: '14px', margin: '0', paddingLeft: '20px' }}>
                <li>URLs are stored in the database for the selected category</li>
                <li>System finds all users interested in this job category</li>
                <li>Applications are automatically created for each user</li>
                <li>Bot will process these applications automatically</li>
                <li>Users will see progress on their dashboards</li>
                <li>You'll get notified if CAPTCHAs need solving</li>
              </ul>
            </div>
          )}
        </div>

        {/* Job Categories Overview */}
        <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '24px', marginBottom: '32px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', margin: '0 0 16px 0' }}>Job Categories</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
            {categories.map((category) => {
              const categoryUrls = jobUrls.filter(url => url.category_id === category.id);
              return (
                <div key={category.id} style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '16px' }}>
                  <h3 style={{ fontWeight: '600', color: '#111827', margin: '0 0 4px 0' }}>{category.category_name}</h3>
                  <p style={{ color: '#6b7280', fontSize: '14px', margin: '0 0 12px 0' }}>{category.description}</p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                    <span style={{ color: '#2563eb' }}>{categoryUrls.length} URLs</span>
                    <span style={{ color: '#16a34a' }}>
                      {categoryUrls.filter(url => url.status === 'active').length} Active
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Test Connection Button */}
        <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '24px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', margin: '0 0 16px 0' }}>Admin System Status</h2>
          <button
            onClick={async () => {
              try {
                const response = await fetch(`${API_BASE}/api/admin/test`, {
                  headers: getAuthHeaders()
                });
                if (response.ok) {
                  const data = await response.json();
                  alert('✅ Admin API is working!\n\n' + JSON.stringify(data, null, 2));
                } else {
                  alert('❌ Admin API test failed: ' + response.status);
                }
              } catch (error) {
                alert('❌ Connection error: ' + error);
              }
            }}
            style={{ 
              backgroundColor: '#16a34a',
              color: 'white', 
              padding: '12px 24px', 
              borderRadius: '6px',
              border: 'none',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            Test Admin API Connection
          </button>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>
            API Base: {API_BASE}
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;