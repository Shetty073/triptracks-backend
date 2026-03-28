{{flutter_js}}
{{flutter_build_config}}

_flutter.loader.load({
  onEntrypointLoaded: async function(engineInitializer) {
    let appRunner = await engineInitializer.initializeEngine({
      // Use HTML renderer so external map tiles load without CORS/canvas-taint issues
      renderer: "html",
    });
    await appRunner.runApp();
  }
});
