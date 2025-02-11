namespace TruckStats;

public partial class AppShell : Shell
{
	public AppShell()
	{
		InitializeComponent();
		// Make sure the MainPage is resolved from DI with its constructor dependencies
		Routing.RegisterRoute("MainPage", typeof(MainPage));

	}
}
