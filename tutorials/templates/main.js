// Mock data for demonstration
const mockJobs = [
    { 
      title: 'React Developer',
      company: 'Apple',
      location: 'Cupertino, CA',
      salary: '$120k - $180k'
    },
    { 
      title: 'Frontend Engineer',
      company: 'Meta',
      location: 'Remote',
      salary: '$130k - $190k'
    },
    { 
      title: 'Full Stack Developer',
      company: 'Amazon',
      location: 'Seattle, WA',
      salary: '$140k - $200k'
    }
  ];
  
  function createDashboard() {
    // Main function to build the job seeker dashboard

    const app = document.querySelector('#app');
    // Selects the div with id "app" to inject the dashboard HTML

    app.innerHTML = `
      <nav class="top-nav">
        <div class="logo">
          <span class="logo-icon">📦</span>
          SHY
        </div>
        <div class="search-container">
          <span class="search-icon">🔍</span>
          <input type="search" placeholder="Search jobs..." class="search-input">
        </div>
        <div class="user-actions">
          <span>🔔</span>
          <span>👤</span>
        </div>
      </nav>
  
      <div class="dashboard">
        <main>
          <section class="profile-section">
            <div class="profile-picture">
              <img src="https://i.pravatar.cc/128" alt="John Doe" width="64" height="64">
            </div>
            <div class="profile-info">
              <h1>John Doe</h1>
              <p>Senior Software Developer</p>
              <div class="location">
                <span>📍</span>
                San Francisco, CA
              </div>
            </div>
            <button class="btn-outline">Edit Profile</button>
          </section>
  
          <section class="documents">
            <h2>Documents</h2>
            <div class="document-item">
              <span class="document-icon">📄</span>
              <div class="document-info">
                <h3>My_CV.pdf</h3>
                <p>Updated 2 days ago</p>
              </div>
              <button class="btn-outline">Edit</button>
            </div>
            <div class="upload-section">
              <p>Upload additional documents</p>
              <button class="btn btn-primary">Upload PDF</button>
            </div>
          </section>
  
          <section class="application-progress">
            <div class="progress-header">
              <div class="company-info">
                <h2>Google</h2>
                <p>Senior Frontend Developer</p>
              </div>
              <span class="status-badge">Interview</span>
            </div>
            <div class="progress-steps">
              <div class="progress-line"></div>
              <div class="step active">
                <div class="step-dot">✓</div>
                <div class="step-label">Applied</div>
              </div>
              <div class="step active">
                <div class="step-dot">✓</div>
                <div class="step-label">Screening</div>
              </div>
              <div class="step active">
                <div class="step-dot">•</div>
                <div class="step-label">Interview</div>
              </div>
              <div class="step">
                <div class="step-dot">•</div>
                <div class="step-label">Offer</div>
              </div>
            </div>
          </section>
        </main>
  
        <aside>
          <section class="suggested-jobs">
            <h2>Suggested Jobs</h2>
            <div id="suggested-jobs"></div>
            <a href="#" class="view-all">View all suggestions</a>
          </section>
          <div class="quick-actions">
            <button class="btn btn-primary">Update CV</button>
            <button class="btn btn-outline">Browse Jobs</button>
          </div>
        </aside>
      </div>
    `;
  
    // Populate suggested jobs
    const suggestedJobsContainer = document.getElementById('suggested-jobs');
    mockJobs.forEach(job => {
      // Loops through mockJobs and creates a card for each job

      const jobElement = document.createElement('div');
      jobElement.className = 'job-card';
      jobElement.innerHTML = `
        <h3 class="job-title">${job.title}</h3>
        <p class="company-name">${job.company}</p>
        <div class="job-location">
          <span>📍</span>
          ${job.location}
        </div>
        <p class="salary-range">${job.salary}</p>
      `;
      suggestedJobsContainer.appendChild(jobElement);
      // Appends each job card to the "suggested-jobs" section

    });
  
    // Add event listeners
    const uploadBtn = document.querySelector('.upload-section .btn-primary');
    uploadBtn.addEventListener('click', () => {
      // Event listener for the upload button

      alert('Upload functionality would go here');
      // Displays a placeholder alert for the upload action

    });
  
    const searchInput = document.querySelector('.search-input');
    searchInput.addEventListener('input', (e) => {
      // Event listener for the search input field

      console.log('Searching for:', e.target.value);
      // Logs the search term to the console

    });
  }
  
  // Initialize the dashboard when the DOM is loaded
  document.addEventListener('DOMContentLoaded', createDashboard);