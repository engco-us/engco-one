CREATE TABLE "tasks" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"title" varchar(200) NOT NULL,
	"outcome" text NOT NULL,
	"project_id" varchar(50) NOT NULL,
	"project_name" varchar(200) NOT NULL,
	"agent_id" varchar(20) NOT NULL,
	"agent_name" varchar(200) NOT NULL,
	"status" varchar(20) DEFAULT 'ready' NOT NULL,
	"attachments" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"analyses" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL
);
