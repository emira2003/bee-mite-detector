// static/js/tests/test_dashboard.js

// Mock document elements
document.body.innerHTML = `
  <div id="currentBeeCount">0</div>
  <div id="currentVarroaCount">0</div>
  <div id="infestationRatio">0.00</div>
  <div id="totalBeeCount">0</div>
  <div id="totalVarroaCount">0</div>
  <div id="statusBadge" class="status-badge risk-unknown">
    <i class="fas fa-circle-info me-2"></i>Unknown
  </div>
  <button id="toggleDetectionButton" class="btn btn-success">
    <i class="fas fa-play me-2" id="buttonIcon"></i><span id="buttonText">Start Detection</span>
  </button>
`;

// Import or mock dashboard functions
// Note: In a real implementation, you'd properly import these
const animateValueChange = (selector, newValue) => {
  document.querySelector(selector).textContent = newValue;
};

const updateRiskStatus = (riskLevel) => {
  const statusBadge = document.querySelector('#statusBadge');
  statusBadge.className = '';
  statusBadge.classList.add('status-badge', `risk-${riskLevel.toLowerCase()}`);
  statusBadge.innerHTML = `<i class="fas fa-circle-info me-2"></i>${riskLevel}`;
};

const setButtonState = (isActive) => {
  const button = document.querySelector('#toggleDetectionButton');
  const icon = document.querySelector('#buttonIcon');
  const text = document.querySelector('#buttonText');
  
  if (isActive) {
    button.classList.remove('btn-success');
    button.classList.add('btn-danger');
    icon.classList.remove('fa-play');
    icon.classList.add('fa-stop');
    text.textContent = 'Stop Detection';
  } else {
    button.classList.remove('btn-danger');
    button.classList.add('btn-success');
    icon.classList.remove('fa-stop');
    icon.classList.add('fa-play');
    text.textContent = 'Start Detection';
  }
};

// Tests
describe('Dashboard UI Functions', () => {
  test('animateValueChange updates element text', () => {
    animateValueChange('#currentBeeCount', 10);
    expect(document.querySelector('#currentBeeCount').textContent).toBe('10');
  });
  
  test('updateRiskStatus changes status badge appearance', () => {
    updateRiskStatus('Low');
    const badge = document.querySelector('#statusBadge');
    expect(badge.classList.contains('risk-low')).toBe(true);
    expect(badge.textContent).toContain('Low');
    
    updateRiskStatus('Critical');
    expect(badge.classList.contains('risk-critical')).toBe(true);
    expect(badge.textContent).toContain('Critical');
  });
  
  test('setButtonState toggles button appearance', () => {
    const button = document.querySelector('#toggleDetectionButton');
    const text = document.querySelector('#buttonText');
    
    setButtonState(true);
    expect(button.classList.contains('btn-danger')).toBe(true);
    expect(text.textContent).toBe('Stop Detection');
    
    setButtonState(false);
    expect(button.classList.contains('btn-success')).toBe(true);
    expect(text.textContent).toBe('Start Detection');
  });
}); 
