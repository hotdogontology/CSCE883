# Monday handoff

Prepared Friday, 2026-11-06. The machine is running the authorized two-pass
statement-correspondence experiment. Do not launch a second GPU job blindly.

**Publishing is blocked.** Work is committed locally. Native Git awaits an
interactive GitHub sign-in; the connected GitHub app can read the repository but
returned HTTP 403 `Resource not accessible by integration` on tree creation.
No successful push is confirmed. The watcher is running in **local-only mode**;
do not expect new snapshots on GitHub. On Monday, authenticate native Git or grant
the app repository write access, then push the saved commits and latest reports.

1. Read [the automatically published results](reports/two-pass/README.md).
   Its timestamp and `latest.json` distinguish observed results from this plan.
2. On this workstation, check `artifacts/two-pass/job.json`, the driver PID in
   `job.pid`, and `watcher.log` / `watcher-errors.log`. Logs and checkpoints are
   local and ignored by Git. A static `running` status alone does not prove the
   process survived; check the PID and recent log/output progress.
3. Inspect `artifacts/two-pass/report.json`, `herald-comparison.csv`,
   `consensus/summary.json`, the second-pass `training.json`, and external outputs.
   The watcher saves small aggregate snapshots, including a final completed/failed
   snapshot. It was launched without `--publish` because write access is blocked.
4. Review class balance and mismatch recall before accuracy. The first-pass
   held-out accuracy rose from 62.50% to 70.54%, but mismatch rejection fell
   from 21/39 to 13/39. Neither teacher is a trusted verifier.
5. Review external flags against actual manuscripts/source definitions and
   theorem scope. No external ground-truth labels or verified release errors
   have been established. Context-limit skips are missing predictions, not NO.

The primary pipeline is: untuned/first-pass Herald inference over 44,553 rows,
agreement-only pseudo-labels (explicitly selected by the user), fresh-original-base
second-pass QLoRA, frozen validation, then untuned/first-/second-pass external
screening. The last tier has three IMO cases and three OpenAI source units from
two manuscripts. It is a qualitative screening pilot. See
[two-pass-experiment.md](two-pass-experiment.md) for exact settings and limitations.

The watcher holds a temporary Windows execution request while observing this
job; it does not permanently change the power plan. Model inference resumes
completed rows with matching inputs/settings. Future long training saves adapter,
optimizer/RNG and progress checkpoints every 512 examples at optimizer boundaries.
Training recovery is manual, not an implemented automatic resume. The driver
stops on failure rather than proceeding with an incomplete model.

No need to re-download models or corpora: inspect local ignored `data/` and
the pinned manifests first. Never commit `.env`, downloads, weights, optimizer
states or bulk prediction logs. The root/project ignore rules cover these.

The user authorized pushing this project work and subsequent generated aggregate
reports. The optional `--publish` mode restricts commits to the report directory;
it is not active. No messages to collaborators or service providers were authorized/sent.
If publishing failed, reports remain local; inspect logs and complete the push
without re-running successful experiment stages.
