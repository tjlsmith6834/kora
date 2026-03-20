// webpack.config.js
const path = require("path");
const webpack = require("webpack");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = (env = {}, argv = {}) => {
  const isProduction = argv.mode === "production";

  return {
    mode: isProduction ? "production" : "development",

    // Entry point for your SDK
    entry: path.resolve(__dirname, "src/index.tsx"),

    // UMD bundle so it works via <script> tag, Node, etc.
    output: {
      path: path.resolve(__dirname, "dist"),
      filename: "kora-apply.js",
      library: {
        name: "KoraApplyWidget",
        type: "umd",
        export: "default",
      },
      globalObject: "this", // so it works in browser & Node-like envs
    },

    // Dev server (used by `npm start`)
    devServer: {
      static: path.resolve(__dirname, "dist"),
      port: 3001,
      host: "0.0.0.0",
      hot: true,
      allowedHosts: "all",
      watchFiles: ["src/**/*"],
    },

    devtool: isProduction ? "source-map" : "eval-source-map",

    resolve: {
      extensions: [".ts", ".tsx", ".js"],
    },

    module: {
      rules: [
        // TypeScript / TSX
        {
          test: /\.(ts|tsx)$/,
          exclude: /node_modules/,
          use: {
            loader: "ts-loader",
            options: {
              configFile: path.resolve(__dirname, "tsconfig.json"),
            },
          },
        },

        // CSS Modules — *.module.css
        {
          test: /\.css$/,
          use: [
            isProduction ? MiniCssExtractPlugin.loader : "style-loader",
            {
              loader: "css-loader",
              options: {
                modules: {
                  auto: /\.module\.css$/,  // <-- treat *.module.css as CSS Modules
                },
              },
            },
          ],
        },
      ],
    },

    plugins: [
      // API base URL by environment
      new webpack.DefinePlugin({
        "process.env.REACT_APP_API_BASE_URL": JSON.stringify(
          isProduction
            ? "https://applyapi.hirekora.com"
            : "http://localhost:8001"
        ),
      }),

      // Extract CSS into separate file in production
      ...(isProduction
        ? [
            new MiniCssExtractPlugin({
              filename: "[name].[contenthash].css",
            }),
          ]
        : []),
    ],
  };
};