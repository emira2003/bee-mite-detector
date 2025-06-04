/**
 * Bee Colony Health Monitor Professional Dashboard
 * Advanced JavaScript functionality with enhanced visualizations
 */

// Global variables for charts and data management
let detectionChart;
let uniqueObjectsChart;
let infestationRatioChart;
let updateInterval;
let detectionActive = false;
let chartUpdateCounter = 0;

// Animation options for counters
const counterAnimationOptions = {
    duration: 1000,
    useEasing: true
};

// Color variables matching our CSS variables
const COLORS = {
    primary: '#ffc107',
    primaryLight: '#fff3cd',
    secondary: '#6f42c1',
    success: '#28a745',
    warning: '#fd7e14',
    danger: '#dc3545',
    info: '#17a2b8',
    muted: '#6c757d',
    chartGridLines: 'rgba(0, 0, 0, 0.05)',
    bee: '#ffc107',
    varroa: '#dc3545',
    ratio: '#6f42c1'
};

/**
 * Initialize all charts with professional styling
 */
function initCharts() {
    console.log("Initializing dashboard charts with enhanced styling");
    
    // Common chart options for consistent styling
    Chart.defaults.font.family = "'Poppins', 'Segoe UI', sans-serif";
    Chart.defaults.color = '#495057';
    Chart.defaults.scale.grid.color = COLORS.chartGridLines;
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0,0,0,0.7)';
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 6;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    
    // Detection trend chart - main time series visualization
    const detectionCtx = document.getElementById('detectionChart').getContext('2d');
    const detectionGradient1 = detectionCtx.createLinearGradient(0, 0, 0, 400);
    detectionGradient1.addColorStop(0, 'rgba(255, 193, 7, 0.4)');
    detectionGradient1.addColorStop(1, 'rgba(255, 193, 7, 0.0)');
    
    const detectionGradient2 = detectionCtx.createLinearGradient(0, 0, 0, 400);
    detectionGradient2.addColorStop(0, 'rgba(220, 53, 69, 0.4)');
    detectionGradient2.addColorStop(1, 'rgba(220, 53, 69, 0.0)');
    
    detectionChart = new Chart(detectionCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Bees',
                    data: [],
                    borderColor: COLORS.bee,
                    backgroundColor: detectionGradient1,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    pointBackgroundColor: COLORS.bee
                },
                {
                    label: 'Varroa Mites',
                    data: [],
                    borderColor: COLORS.varroa,
                    backgroundColor: detectionGradient2,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    pointBackgroundColor: COLORS.varroa
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count',
                        font: {
                            weight: 'bold'
                        },
                        padding: {top: 10, bottom: 10}
                    },
                    ticks: {
                        padding: 10
                    },
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time',
                        font: {
                            weight: 'bold'
                        },
                        padding: {top: 10, bottom: 10}
                    },
                    ticks: {
                        padding: 10,
                        maxRotation: 0,
                        autoSkipPadding: 10
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleFont: {
                        weight: 'bold',
                        size: 13
                    },
                    bodyFont: {
                        size: 12
                    },
                    padding: 12,
                    displayColors: true,
                    usePointStyle: true,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y;
                            return label;
                        }
                    }
                }
            }
        }
    });
    
    // Unique objects chart - bar chart for unique bee/varroa counts
    const uniqueObjectsCtx = document.getElementById('uniqueObjectsChart').getContext('2d');
    uniqueObjectsChart = new Chart(uniqueObjectsCtx, {
        type: 'bar',
        data: {
            labels: ['Bees', 'Varroa Mites'],
            datasets: [{
                label: 'Unique Objects',
                data: [0, 0],
                backgroundColor: [COLORS.bee, COLORS.varroa],
                borderColor: [
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(220, 53, 69, 0.8)'
                ],
                borderWidth: 1,
                borderRadius: 4,
                barPercentage: 0.7,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count',
                        font: {
                            weight: 'bold'
                        },
                        padding: {top: 10, bottom: 10}
                    },
                    ticks: {
                        padding: 10
                    },
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleFont: {
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 12
                    },
                    padding: 12
                }
            }
        }
    });
    
    // Infestation ratio chart - line chart for varroa:bee ratio trends
    const infestationRatioCtx = document.getElementById('infestationRatioChart').getContext('2d');
    const ratioGradient = infestationRatioCtx.createLinearGradient(0, 0, 0, 250);
    ratioGradient.addColorStop(0, 'rgba(111, 66, 193, 0.4)');
    ratioGradient.addColorStop(1, 'rgba(111, 66, 193, 0.0)');
    
    infestationRatioChart = new Chart(infestationRatioCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Varroa:Bee Ratio',
                data: [],
                borderColor: COLORS.ratio,
                backgroundColor: ratioGradient,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 6,
                pointBackgroundColor: COLORS.ratio
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Ratio',
                        font: {
                            weight: 'bold'
                        },
                        padding: {top: 10, bottom: 10}
                    },
                    ticks: {
                        padding: 10,
                        callback: function(value) {
                            return value.toFixed(2);
                        }
                    },
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time',
                        font: {
                            weight: 'bold'
                        },
                        padding: {top: 10, bottom: 10}
                    },
                    ticks: {
                        padding: 10,
                        maxRotation: 0,
                        autoSkipPadding: 10
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                annotation: {
                    annotations: {
                        lowLine: {
                            type: 'line',
                            yMin: 0.05,
                            yMax: 0.05,
                            borderColor: COLORS.success,
                            borderWidth: 1,
                            borderDash: [5, 5],
                            label: {
                                display: false,
                                content: 'Low'
                            }
                        },
                        moderateLine: {
                            type: 'line',
                            yMin: 0.10,
                            yMax: 0.10,
                            borderColor: COLORS.warning,
                            borderWidth: 1,
                            borderDash: [5, 5],
                            label: {
                                display: false,
                                content: 'Moderate'
                            }
                        },
                        highLine: {
                            type: 'line',
                            yMin: 0.15,
                            yMax: 0.15,
                            borderColor: COLORS.danger,
                            borderWidth: 1,
                            borderDash: [5, 5],
                            label: {
                                display: false,
                                content: 'High'
                            }
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleFont: {
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 12
                    },
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y.toFixed(3);
                            return label;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Updates the dashboard with the latest statistics
 * Animates value changes and updates charts
 */
function updateStats() {
    console.log("Updating dashboard statistics");
    
    // Show loading spinner for initial load
    if (!detectionActive) {
        $('#loading-overlay').fadeIn(200);
    }
    
    // Fetch current statistics from API
    $.getJSON('/get_stats', function(data) {
        // Hide loading overlay if visible
        $('#loading-overlay').fadeOut(200);
        
        // Update numeric metrics with animations
        animateValueChange('#currentBeeCount', data.current_bees);
        animateValueChange('#currentVarroaCount', data.current_varroa);
        animateValueChange('#totalBeeCount', data.total_bees);
        animateValueChange('#totalVarroaCount', data.total_varroa);
        animateValueChange('#totalFrames', data.total_frames);
        animateValueChange('#fpsValue', data.fps.toFixed(1));
        
        // Update FPS display
        $('#fpsDisplay').html(`<i class="fas fa-microchip me-2"></i>${data.fps.toFixed(1)} FPS`);
        
        // Update scientific notation displays
        $('#beeSciNotation').text(`n = ${data.current_bees}`);
        $('#varroaSciNotation').text(`n = ${data.current_varroa}`);
        
        // Update infestation ratio with animation
        const ratio = data.infestation_ratio;
        animateValueChange('#infestationRatio', ratio.toFixed(2));
        
        // Update risk status with appropriate styling
        updateRiskStatus(data.infestation_risk_level);
        
        // Update unique objects chart
        updateUniqueObjectsChart(data.unique_bees, data.unique_varroa);
        
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.error("Error fetching statistics:", textStatus, errorThrown);
        $('#loading-overlay').fadeOut(200);
    });
    
    // Get time series data for trend charts
    $.getJSON('/get_time_series', function(data) {
        // Update detection chart with new time series data
        updateDetectionChart(data);
        
        // Update infestation ratio chart
        updateInfestationRatioChart(data);
        
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.error("Error fetching time series data:", textStatus, errorThrown);
    });
}

/**
 * Updates the risk status badge with appropriate styling and animation
 * @param {string} riskLevel - The current risk level (Unknown, Low, Moderate, High, Critical)
 */
function updateRiskStatus(riskLevel) {
    const statusBadge = $('#statusBadge');
    statusBadge.removeClass('risk-unknown risk-low risk-moderate risk-high risk-critical');
    
    let iconClass = 'fa-circle-info';
    let riskClass = 'risk-unknown';
    
    switch(riskLevel) {
        case 'Low':
            iconClass = 'fa-check-circle';
            riskClass = 'risk-low';
            break;
        case 'Moderate':
            iconClass = 'fa-exclamation-circle';
            riskClass = 'risk-moderate';
            break;
        case 'High':
            iconClass = 'fa-exclamation-triangle';
            riskClass = 'risk-high';
            break;
        case 'Critical':
            iconClass = 'fa-radiation';
            riskClass = 'risk-critical';
            break;
        default:
            // Keep defaults for Unknown
    }
    
    // Apply new classes with a fade effect
    statusBadge.fadeOut(200, function() {
        $(this).addClass(riskClass)
               .html(`<i class="fas ${iconClass} me-2"></i>${riskLevel} Risk`)
               .fadeIn(200);
    });
}

/**
 * Animates the change of a displayed value
 * @param {string} selector - jQuery selector for the element
 * @param {number|string} newValue - The new value to display
 */
function animateValueChange(selector, newValue) {
    const element = $(selector);
    const currentValue = parseFloat(element.text()) || 0;
    const targetValue = parseFloat(newValue) || 0;
    
    // Only animate if the value changed
    if (currentValue !== targetValue) {
        $({value: currentValue}).animate({value: targetValue}, {
            duration: 800,
            easing: 'swing',
            step: function() {
                // Format differently based on whether it's an integer or float
                if (Number.isInteger(targetValue)) {
                    element.text(Math.floor(this.value));
                } else {
                    element.text(this.value.toFixed(2));
                }
            },
            complete: function() {
                // Ensure final value is exactly as specified
                element.text(newValue);
            }
        });
    }
}

/**
 * Updates the detection chart with new time series data
 * @param {Object} data - Time series data from API
 */
function updateDetectionChart(data) {
    // Update chart data
    detectionChart.data.labels = data.timestamps;
    detectionChart.data.datasets[0].data = data.bee_counts;
    detectionChart.data.datasets[1].data = data.varroa_counts;
    
    // Use animation based on update frequency
    chartUpdateCounter++;
    detectionChart.options.animation.duration = (chartUpdateCounter % 5 === 0) ? 1000 : 300;
    
    detectionChart.update();
}

/**
 * Updates the unique objects chart with new counts
 * @param {number} beeCount - Number of unique bees
 * @param {number} varroaCount - Number of unique varroa mites
 */
function updateUniqueObjectsChart(beeCount, varroaCount) {
    uniqueObjectsChart.data.datasets[0].data = [beeCount, varroaCount];
    uniqueObjectsChart.update();
}

/**
 * Updates the infestation ratio chart with new time series data
 * @param {Object} data - Time series data from API
 */
function updateInfestationRatioChart(data) {
    infestationRatioChart.data.labels = data.timestamps;
    infestationRatioChart.data.datasets[0].data = data.infestation_ratio;
    
    // Apply different animation duration based on update frequency
    infestationRatioChart.options.animation.duration = (chartUpdateCounter % 5 === 0) ? 1000 : 300;
    
    infestationRatioChart.update();
}

/**
 * Initiates detection process
 */
function startDetection() {
    console.log("Starting detection process...");
    
    // Show loading overlay
    $('#loading-overlay').fadeIn(200);
    
    // Send start command to API
    $.post('/start_detection', function(data) {
        console.log("Detection process response:", data);
        
        // Hide loading overlay after slight delay
        setTimeout(function() {
            $('#loading-overlay').fadeOut(200);
        }, 500);
        
        if (data.status === 'started' || data.status === 'already_running') {
            // Update button and status indicators
            setButtonState(true);
            
            // Update detection status with animation
            $('#detectionStatus').fadeOut(200, function() {
                $(this).removeClass('bg-secondary').addClass('bg-success')
                       .html('<i class="fas fa-video me-2"></i>Active')
                       .fadeIn(200);
            });
            
            // Start periodic updates (every second)
            updateInterval = setInterval(updateStats, 1000);
            
            // Set detection active flag
            detectionActive = true;
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.error("Error starting detection:", textStatus, errorThrown);
        $('#loading-overlay').fadeOut(200);
        
        // Show error message
        alert("Failed to start detection. Please check system console for details.");
    });
}

/**
 * Stops the detection process
 */
function stopDetection() {
    console.log("Stopping detection process...");
    
    // Show loading overlay
    $('#loading-overlay').fadeIn(200);
    
    // Send stop command to API
    $.post('/stop_detection', function(data) {
        console.log("Stop detection response:", data);
        
        // Hide loading overlay after slight delay
        setTimeout(function() {
            $('#loading-overlay').fadeOut(200);
        }, 500);
        
        if (data.status === 'stopped' || data.status === 'already_stopped') {
            // Update button to "Start" state
            setButtonState(false);
            
            // Update detection status with animation
            $('#detectionStatus').fadeOut(200, function() {
                $(this).removeClass('bg-success').addClass('bg-secondary')
                       .html('<i class="fas fa-video-slash me-2"></i>Inactive')
                       .fadeIn(200);
            });
            
            // Stop periodic updates
            clearInterval(updateInterval);
            
            // Set detection active flag
            detectionActive = false;
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.error("Error stopping detection:", textStatus, errorThrown);
        $('#loading-overlay').fadeOut(200);
        
        // Show error message
        alert("Failed to stop detection. Please check system console for details.");
    });
}

/**
 * Sets the button state for the detection toggle button
 * @param {boolean} isActive - Whether detection is active
 */
function setButtonState(isActive) {
    const button = $('#toggleDetectionButton');
    const icon = $('#buttonIcon');
    const text = $('#buttonText');
    
    button.prop('disabled', true);
    
    if (isActive) {
        // Animate to Stop state
        button.fadeOut(200, function() {
            button.removeClass('btn-success').addClass('btn-danger');
            icon.removeClass('fa-play').addClass('fa-stop');
            text.text('Stop Detection');
            button.prop('disabled', false).fadeIn(200);
        });
    } else {
        // Animate to Start state
        button.fadeOut(200, function() {
            button.removeClass('btn-danger').addClass('btn-success');
            icon.removeClass('fa-stop').addClass('fa-play');
            text.text('Start Detection');
            button.prop('disabled', false).fadeIn(200);
        });
    }
}

/**
 * Toggles the detection process state
 */
function toggleDetection() {
    if (detectionActive) {
        stopDetection();
    } else {
        startDetection();
    }
}

/**
 * Document ready initialization
 */
$(document).ready(function() {
    console.log("Initializing Bee Colony Health Monitor Dashboard");
    
    // Initialize charts with professional styling
    initCharts();
    
    // Set up toggle button handler
    $('#toggleDetectionButton').on('click', toggleDetection);
    
    // Add tooltip functionality to all status badges
    $('.status-badge').tooltip({
        placement: 'top'
    });
    
    // Initial stats update
    updateStats();
    
    // Add slight entrance animation for dashboard elements
    $('.dashboard-container').css('opacity', 0).animate({opacity: 1}, 500);
    $('.card').each(function(i) {
        $(this).css({opacity: 0, transform: 'translateY(20px)'})
               .delay(i * 100)
               .animate({opacity: 1, transform: 'translateY(0)'}, 500);
    });
    
    console.log("Dashboard initialization complete");
});
