using Microsoft.Extensions.Logging;
using OpenTelemetry.Trace;
using System.Diagnostics;
using Microsoft.Maui.Devices;

namespace TruckStats
{
    public partial class MainPage : ContentPage
    {
        private readonly ILogger<MainPage> _logger;
        private readonly Tracer _tracer;

        // Parameterless constructor for Xamarin/Maui to use
        public MainPage()
        {
            InitializeComponent();
            _logger = null;  // Optionally initialize as null or use a fallback logger here
            _tracer = null;  // Optionally initialize as null
        }



        // Constructor with DI-injected dependencies
        public MainPage(ILogger<MainPage> logger, Tracer tracer)
        {
            InitializeComponent();
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            _tracer = tracer ?? throw new ArgumentNullException(nameof(tracer));

            // Debugging log to confirm if tracer is being set
            Console.WriteLine(_tracer != null ? "Tracer initialized" : "Tracer is null");
        }


        // Button Click event to log and trace when the user adds a fuel entry
        private void OnAddFuelButtonClicked(object sender, EventArgs e)
        {
            if (_logger == null || _tracer == null)
            {
                // Handle the error or log that the logger/tracer is missing
                Console.WriteLine("Logger or Tracer is null!");
                return;
            }

            // Start a new trace
            using (var span = _tracer.StartSpan("AddFuelEntry"))
            {
                try
                {
                    // Simulate adding fuel entry
                    AddFuelEntry(); // This is a method you might have for adding a fuel record

                    // Log a success message
                    _logger.LogInformation("Fuel entry added successfully.");

                    // Set trace attributes (optional)
                    span.SetAttribute("fuel.added", true);
                    span.SetAttribute("device.id", "android"); // or "ios" depending on platform
                }
                catch (Exception ex)
                {
                    // Log the error
                    _logger?.LogError(ex, "Error while adding fuel entry.");
                    span.SetStatus(Status.Error);
                }
            }
        }


        // Simulate adding a fuel entry (you'd replace this with actual logic)
        private void AddFuelEntry()
        {
            // For demonstration, just a placeholder method
            Debug.WriteLine("Adding fuel entry...");
        }

        // private void OnGetFuelStatsButtonClicked(object sender, EventArgs e)
        // {
        //     if (_tracer == null)
        //     {
        //         _logger.LogError("Tracer is not initialized.");
        //         Debug.WriteLine("Tracer is not initialized.");
        //         return; // Exit if tracer is not available
        //     }

        //     // Proceed with span creation only if tracer is not null
        //     using (var span = _tracer.StartSpan("GetFuelStats"))
        //     {
        //         try
        //         {

        //             // Get the device ID dynamically
        //             string deviceId = GetDeviceId();

        //             // Adding custom attributes to the span
        //             span.SetAttribute("fuel.added", true);  
        //             span.SetAttribute("device.id", deviceId);  // Set the device ID as an attribute

        //             // Simulate fetching fuel stats
        //             var stats = GetFuelStats(span); // Replace with actual logic to fetch stats
        //             Debug.WriteLine("GetFuelStats: ", stats);

        //             // Log success message
        //             //_logger.LogInformation("Fuel stats fetched successfully.");

        //             // Set trace attributes for fuel stats
        //             span.SetAttribute("stats.fuel.fetch.success", true);
        //         }
        //         catch (Exception ex)
        //         {
        //             // Log the error
        //             //_logger.LogError(ex, "Error while fetching fuel stats.");
        //             span.SetStatus(Status.Error);
        //         }
        //     }
        // }

        private void OnGetFuelStatsButtonClicked(object sender, EventArgs e)
        {
            if (_tracer == null)
            {
                _logger?.LogError("Tracer is not initialized.");
                return;
            }

            // Start the main span for the button click action
            using (var telemetrySpan = _tracer.StartSpan("GetFuelStats"))
            {
                try
                {
                    // Get the device ID dynamically
                    string deviceId = GetDeviceId();
                    telemetrySpan.SetAttribute("fuel.added", true);
                    telemetrySpan.SetAttribute("device.id", deviceId);  // Set the device ID as an attribute

                    // Fetch the fuel stats and log them
                    string stats = GetFuelStats(telemetrySpan);  // Pass the telemetrySpan to GetFuelStats
                    _logger?.LogInformation($"Fetched Fuel Stats: {stats}");

                    // Optionally, you can add more attributes to the span
                    telemetrySpan.SetAttribute("device.stats", stats);
                    telemetrySpan.SetAttribute("fuel.stats.fetch.success", true);
                }
                catch (Exception ex)
                {
                    _logger?.LogError(ex, "Error while fetching fuel stats.");
                    telemetrySpan.SetStatus(Status.Error);
                }
            }
        }

        private string GetFuelStats(TelemetrySpan parentTelemetrySpan)
        {
            if (_tracer == null)
            {
                _logger?.LogError("Tracer is not initialized.");
                return string.Empty; // Return empty if tracer is null
            }

            // Start a child span under the provided parent span (no need to rely on Activity.Current)
            using (var telemetryChildSpan = _tracer.StartSpan("GetFuelStatsLevel", parentContext: parentTelemetrySpan.Context))
            {
                try
                {
                    // Generate a random number for fuel stats (for demonstration purposes)
                    Random random = new Random();
                    int randomFuelLevel = random.Next(0, 100);  // Random number between 0 and 100

                    // Log the random fuel level (could be used for tracing or debugging)
                    _logger?.LogInformation($"Generated Random Fuel Level: {randomFuelLevel}");

                    // Set the random number as a custom attribute for the span
                    telemetryChildSpan.SetAttribute("fuel.stats.randomLevel", randomFuelLevel);

                    // Set other optional attributes, like a successful fetch or a timestamp
                    telemetryChildSpan.SetAttribute("fuel.stats.fetch.success", true);
                    telemetryChildSpan.SetAttribute("timestamp", DateTime.UtcNow.ToString("o"));  // Set current timestamp as an attribute

                    // Return the fuel level as a string (could be in any format)
                    return randomFuelLevel.ToString();
                }
                catch (Exception ex)
                {
                    // Log the error if any occurs during fetching
                    _logger?.LogError(ex, "Error while fetching fuel stats.");

                    // Mark the span status as error
                    telemetryChildSpan.SetStatus(Status.Error);

                    return string.Empty;  // Return empty in case of error
                }
            }
        }



        public string GetDeviceId()
        {
            string deviceId = string.Empty;

#if ANDROID
            // For Android, use DeviceInfo to get the unique identifier (IMEI, if available)
            deviceId = Android.Provider.Settings.Secure.GetString(Android.App.Application.Context.ContentResolver, Android.Provider.Settings.Secure.AndroidId);
#elif IOS
            // For iOS, use the UIDevice class to get the identifier
            deviceId = UIKit.UIDevice.CurrentDevice.IdentifierForVendor.ToString();
#endif

            return deviceId;
        }






    }
}
