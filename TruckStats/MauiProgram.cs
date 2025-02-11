using Microsoft.Extensions.Logging;
using OpenTelemetry.Metrics;
using OpenTelemetry.Logs;
using OpenTelemetry.Exporter; // For OTLP exporters
using OpenTelemetry.Trace; // Add this line for Sdk
using OpenTelemetry;
using OpenTelemetry.Resources;


namespace TruckStats
{

    public static class MauiProgram
    {
        public static MauiApp CreateMauiApp()
        {
            var builder = MauiApp.CreateBuilder();

            // Use the TruckStats App as the main application
            builder.UseMauiApp<App>()
                .ConfigureFonts(fonts =>
                {
                    fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                    fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
                });

            // Set up OpenTelemetry for tracing, metrics, and logs
            builder.Services.AddOpenTelemetry()
                .WithTracing(tracing =>
                {
                    tracing
                        .SetResourceBuilder(ResourceBuilder.CreateDefault()
                                                .AddService("TruckStats")  // Custom service name for app traces
                        .AddAttributes(new Dictionary<string, object>
                    {
                            { "service.instance.id", Environment.MachineName },
                            { "service.version", "1.0.0" }}
                            )
                        )  // Set the service name
                        .AddSource("TruckStats")  // Custom source name for app traces
                        .SetSampler(new AlwaysOnSampler())  // Always sample traces (you can adjust sampling)
                        .AddOtlpExporter(options =>
                        {
                            // http://localhost:4317 for iOS Simulator, use IP http://192.168.86.66:4317 address for Android Emulator
                            options.Endpoint = new Uri("http://192.168.86.66:4317");  // Local OpenTelemetry Collector endpoint
                            options.Protocol = OtlpExportProtocol.Grpc;
                        })
                        // .AddOtlpExporter(options =>
                        // {
                        //     // Set the OTLP endpoint (Datadog or Jaeger)
                        //     options.Endpoint = new Uri("https://otlp.datadoghq.com"); // Change for Jaeger if needed
                        //     options.Headers = "DD-API-KEY=<dd-api-key>"; // If using Datadog
                        // })  // Export traces to the console for debugging
                        .AddConsoleExporter();  // Export traces to the console for debugging
                    }
                )
                .WithMetrics(metricsProviderBuilder =>
                {
                    metricsProviderBuilder
                        .AddMeter("TruckStatsMeter")  // Custom meter for TruckStats metrics
                        .AddOtlpExporter(options =>
                        {
                            options.Endpoint = new Uri("http://localhost:4317");  // Local OpenTelemetry Collector endpoint
                        });
                })
                // .WithLogging(builder.Logging.AddOpenTelemetry(options =>
                // {
                //     options.AddOtlpExporter(exporterOptions =>
                //     {
                //         exporterOptions.Endpoint = new Uri("http://localhost:4317");  // Local OpenTelemetry Collector endpoint
                //     });
                // }))
                ;

            // Optional: Configure Datadog Tracing (if you want to send data to Datadog)
            // builder.Services.AddSingleton(serviceProvider =>
            // {
            //     var tracer = Datadog.Trace.Tracer.Instance;
            //     // Configure Datadog API key and Agent URI
            //     var settings = Datadog.Trace.Configuration.TracerSettings.FromDefaultSources();
            //     settings.ServiceName = "TruckStats";
            //     settings.AgentUri = new Uri("http://localhost:8126");  // Local Datadog Agent URI
            //     Datadog.Trace.Tracer.Configure(settings);
            //     return tracer;
            // });


            // Add debug logging during development
#if DEBUG
            builder.Logging.AddDebug();
#endif

            builder.Services.AddSingleton<MainPage>();
            // Register the Tracer
            builder.Services.AddSingleton<Tracer>(sp =>
            {
                var tracerProvider = sp.GetRequiredService<TracerProvider>();
                return tracerProvider.GetTracer("TruckStats");  // Get the tracer from the provider
            });

            return builder.Build();
        }
    }
}