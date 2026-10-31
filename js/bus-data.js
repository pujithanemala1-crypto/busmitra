/**
 * BUSMITRA - Bus Data & Demonstration State
 * Master source of truth for buses, routes, stops, and coordinates.
 */

window.BUSMITRA_DATA = {
  // Demonstration Routes & Stops (Andhra Pradesh Transit Corridor)
  routes: {
    "vijayawada-guntur": {
      id: "vijayawada-guntur",
      name: "Vijayawada to Guntur Express Corridor",
      source: "Vijayawada",
      destination: "Guntur",
      distanceKm: 34.5,
      estimatedTimeMin: 75,
      stops: [
        { id: "vja_pnbs", name: "Vijayawada (PNBS Bus Station)", lat: 16.5062, lng: 80.6480, order: 1, scheduledTime: "10:30 AM" },
        { id: "vja_enikepadu", name: "Enikepadu Junction", lat: 16.5186, lng: 80.6860, order: 2, scheduledTime: "10:45 AM" },
        { id: "vja_gannavaram", name: "Gannavaram Bypass", lat: 16.5369, lng: 80.8037, order: 3, scheduledTime: "11:00 AM" },
        { id: "mangalagiri", name: "Mangalagiri (AIIMS Bypass)", lat: 16.4357, lng: 80.5645, order: 4, scheduledTime: "11:15 AM" },
        { id: "tadepalli", name: "Tadepalli Highway", lat: 16.4812, lng: 80.6053, order: 5, scheduledTime: "11:30 AM" },
        { id: "guntur_ntr", name: "Guntur (NTR Bus Terminal)", lat: 16.3067, lng: 80.4365, order: 6, scheduledTime: "11:45 AM" }
      ],
      // Waypoint track polyline
      waypoints: [
        [16.5062, 80.6480],
        [16.5120, 80.6650],
        [16.5186, 80.6860],
        [16.5280, 80.7450],
        [16.5369, 80.8037],
        [16.4950, 80.6900],
        [16.4812, 80.6053],
        [16.4520, 80.5820],
        [16.4357, 80.5645],
        [16.3750, 80.5100],
        [16.3300, 80.4650],
        [16.3067, 80.4365]
      ]
    }
  },

  // Demonstration Buses (As strictly specified in Prompt Section 6)
  buses: [
    {
      id: "AP161234",
      number: "AP 16 1234",
      name: "Amaravati Express",
      serviceType: "Express",
      routeId: "vijayawada-guntur",
      source: "Vijayawada",
      destination: "Guntur",
      departureTime: "10:30 AM",
      expectedArrivalTime: "11:45 AM",
      duration: "1 hr 15 min",
      capacity: 50,
      currentPassengers: 25,
      // IR sensor entry/exit hardware counts
      sensorInCount: 32,
      sensorOutCount: 7,
      currentStopIndex: 2, // Near Gannavaram
      currentLocationName: "Mangalagiri Highway (Km 18)",
      distanceToBoardingKm: 3.2,
      gpsStatus: "ACTIVE",
      lastUpdated: "Just now",
      sensorStatus: "CONNECTED",
      esp32Status: "ONLINE",
      prediction: {
        nextStop: "Mangalagiri (AIIMS)",
        predictedOccupancy: 31,
        expectedBoarding: 9,
        expectedAlighting: 3,
        confidence: "94%",
        dataSource: "Historical IR Patterns + Commuter Card Swipes"
      }
    },
    {
      id: "AP165678",
      number: "AP 16 5678",
      name: "Krishnaveni Luxury",
      serviceType: "Super Luxury",
      routeId: "vijayawada-guntur",
      source: "Vijayawada",
      destination: "Guntur",
      departureTime: "10:45 AM",
      expectedArrivalTime: "12:00 PM",
      duration: "1 hr 15 min",
      capacity: 50,
      currentPassengers: 40,
      sensorInCount: 46,
      sensorOutCount: 6,
      currentStopIndex: 1, // Near Enikepadu
      currentLocationName: "Tadepalli Flyover",
      distanceToBoardingKm: 7.8,
      gpsStatus: "ACTIVE",
      lastUpdated: "1 min ago",
      sensorStatus: "CONNECTED",
      esp32Status: "ONLINE",
      prediction: {
        nextStop: "Enikepadu Junction",
        predictedOccupancy: 44,
        expectedBoarding: 7,
        expectedAlighting: 3,
        confidence: "88%",
        dataSource: "Historical IR Sensor Averages"
      }
    },
    {
      id: "AP169012",
      number: "AP 16 9012",
      name: "Capital Metro City",
      serviceType: "City Express",
      routeId: "vijayawada-guntur",
      source: "Vijayawada",
      destination: "Guntur",
      departureTime: "11:00 AM",
      expectedArrivalTime: "12:20 PM",
      duration: "1 hr 20 min",
      capacity: 50,
      currentPassengers: 55, // Over capacity (standees)
      sensorInCount: 68,
      sensorOutCount: 13,
      currentStopIndex: 3, // At Mangalagiri
      currentLocationName: "Mangalagiri Bus Shelter",
      distanceToBoardingKm: 0.8,
      gpsStatus: "ACTIVE",
      lastUpdated: "2 mins ago",
      sensorStatus: "CONNECTED",
      esp32Status: "ONLINE",
      prediction: {
        nextStop: "Tadepalli Highway",
        predictedOccupancy: 52,
        expectedBoarding: 4,
        expectedAlighting: 7,
        confidence: "91%",
        dataSource: "Real-time Alighting Sensor History"
      }
    },
    {
      id: "AP163456",
      number: "AP 16 3456",
      name: "Kanakadurga Deluxe",
      serviceType: "Metro Deluxe",
      routeId: "vijayawada-guntur",
      source: "Vijayawada",
      destination: "Guntur",
      departureTime: "11:15 AM",
      expectedArrivalTime: "12:35 PM",
      duration: "1 hr 20 min",
      capacity: 50,
      currentPassengers: 42,
      sensorInCount: 51,
      sensorOutCount: 9,
      currentStopIndex: 0,
      currentLocationName: "Vijayawada PNBS Platform 4",
      distanceToBoardingKm: 14.5,
      gpsStatus: "ACTIVE",
      lastUpdated: "Just now",
      sensorStatus: "CONNECTED",
      esp32Status: "ONLINE",
      prediction: {
        nextStop: "Enikepadu Junction",
        predictedOccupancy: 46,
        expectedBoarding: 8,
        expectedAlighting: 4,
        confidence: "86%",
        dataSource: "Sensor Trend Matrix"
      }
    }
  ],

  // Popular Destinations for quick selection
  popularDestinations: [
    { name: "Guntur", distance: "34 km", avgBuses: "Every 10 mins" },
    { name: "Mangalagiri", distance: "14 km", avgBuses: "Every 8 mins" },
    { name: "Gannavaram", distance: "21 km", avgBuses: "Every 12 mins" },
    { name: "Tenali", distance: "38 km", avgBuses: "Every 15 mins" },
    { name: "Eluru", distance: "58 km", avgBuses: "Every 20 mins" }
  ]
};

/**
 * Utility helper to compute dynamically calculated occupancy and crowd levels
 * Formula:
 * Available Seats = Max(0, Capacity - Current Passengers)
 * Occupancy % = (Current Passengers / Capacity) * 100
 * Crowd:
 *  0 - 40% => LOW
 *  >40% - 75% => MODERATE
 *  >75% - 100% => HIGH
 *  >100% => OVERCROWDED
 */
window.calculateBusMetrics = function(bus) {
  const capacity = Number(bus.capacity) || 50;
  // If sensor counts exist, Current Passengers = Total IN - Total OUT
  let passengers = bus.currentPassengers;
  if (typeof bus.sensorInCount === 'number' && typeof bus.sensorOutCount === 'number') {
    passengers = Math.max(0, bus.sensorInCount - bus.sensorOutCount);
  }

  const availableSeats = Math.max(0, capacity - passengers);
  const occupancyPercent = Math.round((passengers / capacity) * 100);

  let crowdLevel = "LOW";
  let crowdClass = "low";
  let crowdColor = "#16A34A";

  if (occupancyPercent <= 40) {
    crowdLevel = "LOW";
    crowdClass = "low";
    crowdColor = "#16A34A";
  } else if (occupancyPercent <= 75) {
    crowdLevel = "MODERATE";
    crowdClass = "moderate";
    crowdColor = "#D97706";
  } else if (occupancyPercent <= 100) {
    crowdLevel = "HIGH";
    crowdClass = "high";
    crowdColor = "#DC2626";
  } else {
    crowdLevel = "OVERCROWDED";
    crowdClass = "overcrowded";
    crowdColor = "#991B1B";
  }

  return {
    capacity,
    currentPassengers: passengers,
    availableSeats,
    occupancyPercent,
    crowdLevel,
    crowdClass,
    crowdColor
  };
};

/**
 * Get bus by ID with fresh calculated metrics
 */
window.getBusById = function(busId) {
  const bus = window.BUSMITRA_DATA.buses.find(b => b.id === busId || b.number === busId);
  if (!bus) return null;
  const metrics = window.calculateBusMetrics(bus);
  return { ...bus, ...metrics };
};
