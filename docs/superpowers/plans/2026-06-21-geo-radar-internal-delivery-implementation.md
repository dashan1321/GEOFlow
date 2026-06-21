# GEO Radar Internal Delivery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build GEO Radar as an internal sales and delivery layer on top of the existing GEOFlow visibility module.

**Architecture:** Extend the existing Laravel `geo_visibility_*` module rather than creating a new app. Add sales-oriented project fields, conversion targets, prompt generation, run scopes, result snapshots, and report publishing around the existing `GeoVisibilityRunService`.

**Tech Stack:** Laravel 12, Blade, Tailwind, PostgreSQL, Laravel queues where available, existing `AiModel` provider configuration, existing admin authentication.

---

## File Structure

Create:

- `GEOFlow-docker/database/migrations/2026_06_21_000000_upgrade_geo_visibility_for_radar.php`
- `GEOFlow-docker/app/Models/GeoVisibilityConversionTarget.php`
- `GEOFlow-docker/app/Models/GeoVisibilitySnapshot.php`
- `GEOFlow-docker/app/Models/GeoVisibilityReport.php`
- `GEOFlow-docker/app/Services/GeoFlow/GeoPromptGeneratorService.php`
- `GEOFlow-docker/app/Services/GeoFlow/GeoRadarScoringService.php`
- `GEOFlow-docker/app/Services/GeoFlow/GeoRadarReportService.php`
- `GEOFlow-docker/resources/views/admin/geo-visibility/report.blade.php`
- `GEOFlow-docker/resources/views/admin/geo-visibility/snapshot.blade.php`
- `GEOFlow-docker/tests/Feature/AdminGeoRadarProjectTest.php`
- `GEOFlow-docker/tests/Feature/AdminGeoRadarReportTest.php`
- `GEOFlow-docker/tests/Unit/GeoPromptGeneratorServiceTest.php`
- `GEOFlow-docker/tests/Unit/GeoRadarScoringServiceTest.php`

Modify:

- `GEOFlow-docker/routes/web.php`
- `GEOFlow-docker/app/Http/Controllers/Admin/GeoVisibilityController.php`
- `GEOFlow-docker/app/Models/GeoVisibilityProject.php`
- `GEOFlow-docker/app/Models/GeoVisibilityResult.php`
- `GEOFlow-docker/app/Models/GeoVisibilityRun.php`
- `GEOFlow-docker/app/Services/GeoFlow/GeoVisibilityRunService.php`
- `GEOFlow-docker/resources/views/admin/geo-visibility/index.blade.php`
- `GEOFlow-docker/resources/views/admin/geo-visibility/show.blade.php`

---

### Task 1: Add GEO Radar Storage

**Files:**

- Create: `GEOFlow-docker/database/migrations/2026_06_21_000000_upgrade_geo_visibility_for_radar.php`
- Create: `GEOFlow-docker/app/Models/GeoVisibilityConversionTarget.php`
- Create: `GEOFlow-docker/app/Models/GeoVisibilitySnapshot.php`
- Create: `GEOFlow-docker/app/Models/GeoVisibilityReport.php`
- Modify: `GEOFlow-docker/app/Models/GeoVisibilityProject.php`
- Modify: `GEOFlow-docker/app/Models/GeoVisibilityResult.php`
- Modify: `GEOFlow-docker/app/Models/GeoVisibilityRun.php`
- Test: `GEOFlow-docker/tests/Feature/AdminGeoRadarProjectTest.php`

- [ ] **Step 1: Write the failing model/storage test**

Create `GEOFlow-docker/tests/Feature/AdminGeoRadarProjectTest.php`:

```php
<?php

namespace Tests\Feature;

use App\Models\Admin;
use App\Models\GeoVisibilityProject;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class AdminGeoRadarProjectTest extends TestCase
{
    use RefreshDatabase;

    public function test_project_stores_sales_delivery_fields_and_conversion_targets(): void
    {
        $admin = Admin::factory()->create();

        $response = $this->actingAs($admin, 'admin')->post(route('admin.geo-visibility.store'), [
            'client_name' => 'Acme Foods',
            'name' => 'Acme GEO Radar',
            'brand_name' => 'Acme',
            'website_url' => 'https://example.com',
            'industry' => '食品',
            'region' => '上海',
            'status' => 'lead',
            'description' => '高端食品品牌',
            'competitors_text' => "Competitor A\nCompetitor B",
            'conversion_targets_text' => "website|官网|https://example.com\nphone|销售电话|400-000-0000",
            'prompts_text' => '上海有哪些高端食品品牌推荐？',
        ]);

        $response->assertRedirect(route('admin.geo-visibility.index'));

        $project = GeoVisibilityProject::query()->where('brand_name', 'Acme')->firstOrFail();

        $this->assertSame('Acme Foods', $project->client_name);
        $this->assertSame('上海', $project->region);
        $this->assertSame('lead', $project->status);
        $this->assertCount(2, $project->conversionTargets);
    }
}
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=AdminGeoRadarProjectTest
```

Expected: FAIL because the new columns, relationship, and conversion target model do not exist.

- [ ] **Step 3: Add the migration**

Create `GEOFlow-docker/database/migrations/2026_06_21_000000_upgrade_geo_visibility_for_radar.php`:

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('geo_visibility_projects', function (Blueprint $table): void {
            $table->string('client_name', 160)->nullable()->after('id');
            $table->string('region', 120)->nullable()->after('industry');
            $table->string('status', 40)->default('lead')->after('description');
            $table->string('contact_name', 120)->nullable()->after('status');
            $table->string('contact_phone', 120)->nullable()->after('contact_name');
            $table->foreignId('owner_id')->nullable()->after('contact_phone')->constrained('admins')->nullOnDelete();
        });

        Schema::table('geo_visibility_runs', function (Blueprint $table): void {
            $table->string('mode', 40)->default('quick')->after('project_id');
            $table->unsignedTinyInteger('average_position')->nullable()->after('brand_mention_rate');
            $table->unsignedTinyInteger('platform_coverage')->default(0)->after('competitor_pressure');
            $table->unsignedTinyInteger('conversion_exposure')->default(0)->after('platform_coverage');
            $table->unsignedTinyInteger('citation_coverage')->default(0)->after('conversion_exposure');
        });

        Schema::table('geo_visibility_results', function (Blueprint $table): void {
            $table->mediumText('answer_text')->nullable()->after('provider_region');
            $table->json('conversion_hits')->nullable()->after('citation_urls');
            $table->json('risk_tags')->nullable()->after('conversion_hits');
        });

        Schema::create('geo_visibility_conversion_targets', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('project_id')->constrained('geo_visibility_projects')->cascadeOnDelete();
            $table->string('type', 40);
            $table->string('label', 120);
            $table->string('value', 500);
            $table->timestamps();
            $table->index(['project_id', 'type']);
        });

        Schema::create('geo_visibility_snapshots', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('result_id')->constrained('geo_visibility_results')->cascadeOnDelete();
            $table->string('public_token', 80)->unique();
            $table->string('title', 200);
            $table->longText('html_content');
            $table->timestamp('revoked_at')->nullable();
            $table->timestamps();
        });

        Schema::create('geo_visibility_reports', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('project_id')->constrained('geo_visibility_projects')->cascadeOnDelete();
            $table->foreignId('run_id')->nullable()->constrained('geo_visibility_runs')->nullOnDelete();
            $table->string('type', 40)->default('sales');
            $table->string('title', 200);
            $table->string('public_token', 80)->unique();
            $table->longText('report_html');
            $table->string('pdf_path', 500)->nullable();
            $table->timestamp('revoked_at')->nullable();
            $table->timestamps();
            $table->index(['project_id', 'type']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('geo_visibility_reports');
        Schema::dropIfExists('geo_visibility_snapshots');
        Schema::dropIfExists('geo_visibility_conversion_targets');

        Schema::table('geo_visibility_results', function (Blueprint $table): void {
            $table->dropColumn(['answer_text', 'conversion_hits', 'risk_tags']);
        });

        Schema::table('geo_visibility_runs', function (Blueprint $table): void {
            $table->dropColumn(['mode', 'average_position', 'platform_coverage', 'conversion_exposure', 'citation_coverage']);
        });

        Schema::table('geo_visibility_projects', function (Blueprint $table): void {
            $table->dropConstrainedForeignId('owner_id');
            $table->dropColumn(['client_name', 'region', 'status', 'contact_name', 'contact_phone']);
        });
    }
};
```

- [ ] **Step 4: Add models and relationships**

Create `GEOFlow-docker/app/Models/GeoVisibilityConversionTarget.php`:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class GeoVisibilityConversionTarget extends Model
{
    protected $fillable = ['project_id', 'type', 'label', 'value'];

    public function project(): BelongsTo
    {
        return $this->belongsTo(GeoVisibilityProject::class, 'project_id');
    }
}
```

Create `GEOFlow-docker/app/Models/GeoVisibilitySnapshot.php`:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class GeoVisibilitySnapshot extends Model
{
    protected $fillable = ['result_id', 'public_token', 'title', 'html_content', 'revoked_at'];

    protected function casts(): array
    {
        return ['revoked_at' => 'datetime'];
    }

    public function result(): BelongsTo
    {
        return $this->belongsTo(GeoVisibilityResult::class, 'result_id');
    }
}
```

Create `GEOFlow-docker/app/Models/GeoVisibilityReport.php`:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class GeoVisibilityReport extends Model
{
    protected $fillable = ['project_id', 'run_id', 'type', 'title', 'public_token', 'report_html', 'pdf_path', 'revoked_at'];

    protected function casts(): array
    {
        return ['revoked_at' => 'datetime'];
    }

    public function project(): BelongsTo
    {
        return $this->belongsTo(GeoVisibilityProject::class, 'project_id');
    }

    public function run(): BelongsTo
    {
        return $this->belongsTo(GeoVisibilityRun::class, 'run_id');
    }
}
```

Modify `GeoVisibilityProject` fillable and relationships:

```php
protected $fillable = [
    'client_name',
    'name',
    'brand_name',
    'website_url',
    'industry',
    'region',
    'description',
    'status',
    'contact_name',
    'contact_phone',
    'owner_id',
    'is_active',
    'last_run_at',
    'latest_score',
];

public function conversionTargets(): HasMany
{
    return $this->hasMany(GeoVisibilityConversionTarget::class, 'project_id');
}

public function reports(): HasMany
{
    return $this->hasMany(GeoVisibilityReport::class, 'project_id')->latest();
}
```

Modify `GeoVisibilityRun` fillable/casts to include:

```php
'mode',
'average_position',
'platform_coverage',
'conversion_exposure',
'citation_coverage',
```

Modify `GeoVisibilityResult` fillable/casts to include:

```php
'answer_text',
'conversion_hits',
'risk_tags',
```

- [ ] **Step 5: Update project storage to parse conversion targets**

In `GeoVisibilityController::store()`, add validation fields:

```php
'client_name' => ['nullable', 'string', 'max:160'],
'region' => ['nullable', 'string', 'max:120'],
'status' => ['nullable', 'in:lead,quoted,won,active,paused,lost'],
'contact_name' => ['nullable', 'string', 'max:120'],
'contact_phone' => ['nullable', 'string', 'max:120'],
'conversion_targets_text' => ['nullable', 'string'],
```

When creating the project, set:

```php
'client_name' => trim((string) ($payload['client_name'] ?? '')),
'region' => trim((string) ($payload['region'] ?? '')),
'status' => (string) ($payload['status'] ?? 'lead'),
'contact_name' => trim((string) ($payload['contact_name'] ?? '')),
'contact_phone' => trim((string) ($payload['contact_phone'] ?? '')),
'owner_id' => $request->user('admin')?->id,
```

Add a private parser:

```php
private function parseConversionTargets(string $text): array
{
    return collect(preg_split('/[\r\n]+/', $text) ?: [])
        ->map(static fn (string $line): string => trim($line))
        ->filter(static fn (string $line): bool => $line !== '')
        ->map(function (string $line): array {
            $parts = array_pad(array_map('trim', explode('|', $line, 3)), 3, '');

            return [
                'type' => $parts[0] !== '' ? $parts[0] : 'custom',
                'label' => $parts[1] !== '' ? $parts[1] : $parts[0],
                'value' => $parts[2] !== '' ? $parts[2] : $line,
            ];
        })
        ->filter(static fn (array $target): bool => $target['value'] !== '')
        ->values()
        ->all();
}
```

Inside the transaction after project creation:

```php
foreach ($this->parseConversionTargets((string) ($payload['conversion_targets_text'] ?? '')) as $target) {
    $project->conversionTargets()->create($target);
}
```

- [ ] **Step 6: Run the test to verify it passes**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=AdminGeoRadarProjectTest
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add GEOFlow-docker/database/migrations/2026_06_21_000000_upgrade_geo_visibility_for_radar.php \
  GEOFlow-docker/app/Models/GeoVisibilityConversionTarget.php \
  GEOFlow-docker/app/Models/GeoVisibilitySnapshot.php \
  GEOFlow-docker/app/Models/GeoVisibilityReport.php \
  GEOFlow-docker/app/Models/GeoVisibilityProject.php \
  GEOFlow-docker/app/Models/GeoVisibilityRun.php \
  GEOFlow-docker/app/Models/GeoVisibilityResult.php \
  GEOFlow-docker/app/Http/Controllers/Admin/GeoVisibilityController.php \
  GEOFlow-docker/tests/Feature/AdminGeoRadarProjectTest.php
git commit -m "feat: add geo radar storage"
```

---

### Task 2: Add Prompt Generation

**Files:**

- Create: `GEOFlow-docker/app/Services/GeoFlow/GeoPromptGeneratorService.php`
- Modify: `GEOFlow-docker/app/Http/Controllers/Admin/GeoVisibilityController.php`
- Modify: `GEOFlow-docker/routes/web.php`
- Modify: `GEOFlow-docker/resources/views/admin/geo-visibility/show.blade.php`
- Test: `GEOFlow-docker/tests/Unit/GeoPromptGeneratorServiceTest.php`

- [ ] **Step 1: Write the failing unit test**

Create `GEOFlow-docker/tests/Unit/GeoPromptGeneratorServiceTest.php`:

```php
<?php

namespace Tests\Unit;

use App\Services\GeoFlow\GeoPromptGeneratorService;
use PHPUnit\Framework\TestCase;

class GeoPromptGeneratorServiceTest extends TestCase
{
    public function test_generates_sales_ready_prompt_set(): void
    {
        $service = new GeoPromptGeneratorService();

        $prompts = $service->generate(
            brandName: 'Acme',
            industry: '食品',
            region: '上海',
            competitors: ['Competitor A'],
            limit: 12
        );

        $this->assertCount(12, $prompts);
        $this->assertContains('Acme怎么样？', array_column($prompts, 'question'));
        $this->assertContains('上海有哪些食品品牌推荐？', array_column($prompts, 'question'));
        $this->assertContains('Acme和Competitor A哪个更适合？', array_column($prompts, 'question'));
        $this->assertContains('品牌查询', array_column($prompts, 'intent'));
        $this->assertContains('竞品对比', array_column($prompts, 'intent'));
    }
}
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=GeoPromptGeneratorServiceTest
```

Expected: FAIL because `GeoPromptGeneratorService` does not exist.

- [ ] **Step 3: Implement the generator**

Create `GEOFlow-docker/app/Services/GeoFlow/GeoPromptGeneratorService.php`:

```php
<?php

namespace App\Services\GeoFlow;

class GeoPromptGeneratorService
{
    /**
     * @param  array<int, string>  $competitors
     * @return array<int, array{question: string, intent: string}>
     */
    public function generate(string $brandName, string $industry, string $region = '', array $competitors = [], int $limit = 30): array
    {
        $brand = trim($brandName);
        $market = trim($industry) !== '' ? trim($industry) : '服务';
        $area = trim($region);
        $prefix = $area !== '' ? $area : '国内';

        $templates = [
            ['question' => "{$brand}怎么样？", 'intent' => '品牌查询'],
            ['question' => "{$brand}靠谱吗？", 'intent' => '品牌信任'],
            ['question' => "{$prefix}有哪些{$market}品牌推荐？", 'intent' => '地域推荐'],
            ['question' => "{$market}怎么选？", 'intent' => '购买决策'],
            ['question' => "做{$market}应该找哪家公司？", 'intent' => '行业推荐'],
            ['question' => "{$brand}的优势是什么？", 'intent' => '品牌认知'],
            ['question' => "{$brand}适合哪些客户？", 'intent' => '场景匹配'],
            ['question' => "{$brand}有没有官网或联系方式？", 'intent' => '转化意图'],
        ];

        foreach ($competitors as $competitor) {
            $name = trim($competitor);
            if ($name !== '') {
                $templates[] = ['question' => "{$brand}和{$name}哪个更适合？", 'intent' => '竞品对比'];
                $templates[] = ['question' => "{$brand}相比{$name}有什么区别？", 'intent' => '竞品对比'];
            }
        }

        return collect($templates)
            ->unique('question')
            ->take(max(1, $limit))
            ->values()
            ->all();
    }
}
```

- [ ] **Step 4: Add controller action and route**

In `routes/web.php`, inside `geo-visibility` group:

```php
Route::post('{projectId}/prompts/generate', [GeoVisibilityController::class, 'generatePrompts'])->name('prompts.generate')->whereNumber('projectId');
```

Inject `GeoPromptGeneratorService` into the controller constructor:

```php
public function __construct(
    private readonly GeoVisibilityRunService $runService,
    private readonly GeoPromptGeneratorService $promptGenerator,
) {}
```

Add action:

```php
public function generatePrompts(int $projectId): RedirectResponse
{
    $project = GeoVisibilityProject::query()->with(['competitors', 'prompts'])->whereKey($projectId)->firstOrFail();
    $existing = $project->prompts->pluck('question')->all();
    $generated = $this->promptGenerator->generate(
        brandName: $project->brand_name,
        industry: (string) $project->industry,
        region: (string) $project->region,
        competitors: $project->competitors->pluck('name')->all(),
        limit: 30,
    );

    $sort = (int) $project->prompts()->max('sort_order');
    foreach ($generated as $prompt) {
        if (in_array($prompt['question'], $existing, true)) {
            continue;
        }

        $project->prompts()->create([
            'question' => $prompt['question'],
            'intent' => $prompt['intent'],
            'locale' => 'zh-CN',
            'is_active' => true,
            'sort_order' => ++$sort,
        ]);
    }

    return redirect()->route('admin.geo-visibility.show', ['projectId' => $project->id])->with('message', '问题词已生成。');
}
```

- [ ] **Step 5: Add button to project page**

In `show.blade.php` next to run buttons:

```blade
<form method="POST" action="{{ route('admin.geo-visibility.prompts.generate', ['projectId' => $project->id]) }}">
    @csrf
    <button type="submit" class="inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
        <i data-lucide="sparkles" class="mr-2 h-4 w-4"></i>
        生成问题词
    </button>
</form>
```

- [ ] **Step 6: Run tests**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=GeoPromptGeneratorServiceTest
php artisan test --filter=AdminGeoRadarProjectTest
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add GEOFlow-docker/app/Services/GeoFlow/GeoPromptGeneratorService.php \
  GEOFlow-docker/app/Http/Controllers/Admin/GeoVisibilityController.php \
  GEOFlow-docker/routes/web.php \
  GEOFlow-docker/resources/views/admin/geo-visibility/show.blade.php \
  GEOFlow-docker/tests/Unit/GeoPromptGeneratorServiceTest.php
git commit -m "feat: generate geo radar prompts"
```

---

### Task 3: Add GEO Radar Scoring

**Files:**

- Create: `GEOFlow-docker/app/Services/GeoFlow/GeoRadarScoringService.php`
- Modify: `GEOFlow-docker/app/Services/GeoFlow/GeoVisibilityRunService.php`
- Test: `GEOFlow-docker/tests/Unit/GeoRadarScoringServiceTest.php`

- [ ] **Step 1: Write the failing scoring test**

Create `GEOFlow-docker/tests/Unit/GeoRadarScoringServiceTest.php`:

```php
<?php

namespace Tests\Unit;

use App\Services\GeoFlow\GeoRadarScoringService;
use PHPUnit\Framework\TestCase;

class GeoRadarScoringServiceTest extends TestCase
{
    public function test_calculates_weighted_geo_score(): void
    {
        $service = new GeoRadarScoringService();

        $score = $service->score([
            'brand_mention_rate' => 70,
            'average_position_score' => 80,
            'platform_coverage' => 60,
            'competitor_pressure_inverse' => 75,
            'conversion_exposure' => 40,
            'citation_coverage' => 50,
        ]);

        $this->assertSame(68, $score);
    }
}
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=GeoRadarScoringServiceTest
```

Expected: FAIL because the service does not exist.

- [ ] **Step 3: Implement scoring service**

Create `GEOFlow-docker/app/Services/GeoFlow/GeoRadarScoringService.php`:

```php
<?php

namespace App\Services\GeoFlow;

class GeoRadarScoringService
{
    /**
     * @param  array{brand_mention_rate: int, average_position_score: int, platform_coverage: int, competitor_pressure_inverse: int, conversion_exposure: int, citation_coverage: int}  $components
     */
    public function score(array $components): int
    {
        $weighted =
            ($components['brand_mention_rate'] * 0.30) +
            ($components['average_position_score'] * 0.20) +
            ($components['platform_coverage'] * 0.15) +
            ($components['competitor_pressure_inverse'] * 0.15) +
            ($components['conversion_exposure'] * 0.10) +
            ($components['citation_coverage'] * 0.10);

        return max(0, min(100, (int) round($weighted)));
    }

    public function positionScore(?float $averagePosition): int
    {
        if ($averagePosition === null || $averagePosition <= 0) {
            return 0;
        }

        return max(0, min(100, (int) round(110 - ($averagePosition * 20))));
    }

    public function level(int $score): string
    {
        return match (true) {
            $score < 40 => 'AI 搜索弱可见',
            $score < 60 => '有基础曝光，但不稳定',
            $score < 80 => '具备行业竞争力',
            default => 'AI 搜索强势品牌',
        };
    }
}
```

- [ ] **Step 4: Wire scoring into run summary**

Inject `GeoRadarScoringService` into `GeoVisibilityRunService`:

```php
public function __construct(
    private readonly ApiKeyCrypto $apiKeyCrypto,
    private readonly GeoRadarScoringService $scoring,
) {}
```

In `summarizeRun()`, compute:

```php
$results = $run->results()->get();
$resultCount = max(1, $results->count());
$brandMentionRate = (int) round(($results->where('brand_mentioned', true)->count() / $resultCount) * 100);
$averagePosition = $results->whereNotNull('brand_position')->avg('brand_position');
$platformCoverage = (int) round(($results->where('brand_mentioned', true)->pluck('provider_key')->unique()->count() / max(1, $results->pluck('provider_key')->unique()->count())) * 100);
$competitorPressure = (int) round(($results->filter(fn ($result) => count($result->competitor_mentions ?? []) > 0)->count() / $resultCount) * 100);
$conversionExposure = (int) round(($results->filter(fn ($result) => count($result->conversion_hits ?? []) > 0)->count() / $resultCount) * 100);
$citationCoverage = (int) round(($results->filter(fn ($result) => count($result->citation_urls ?? []) > 0)->count() / $resultCount) * 100);

$geoScore = $this->scoring->score([
    'brand_mention_rate' => $brandMentionRate,
    'average_position_score' => $this->scoring->positionScore($averagePosition),
    'platform_coverage' => $platformCoverage,
    'competitor_pressure_inverse' => 100 - $competitorPressure,
    'conversion_exposure' => $conversionExposure,
    'citation_coverage' => $citationCoverage,
]);
```

Update run:

```php
$run->update([
    'result_count' => $results->count(),
    'visibility_score' => $geoScore,
    'brand_mention_rate' => $brandMentionRate,
    'average_position' => $averagePosition ? (int) round($averagePosition) : null,
    'competitor_pressure' => $competitorPressure,
    'platform_coverage' => $platformCoverage,
    'conversion_exposure' => $conversionExposure,
    'citation_coverage' => $citationCoverage,
    'summary' => [
        'mode' => $mode,
        'level' => $this->scoring->level($geoScore),
        'domestic_score' => $geoScore,
        'components' => compact('brandMentionRate', 'platformCoverage', 'competitorPressure', 'conversionExposure', 'citationCoverage'),
    ],
]);
```

- [ ] **Step 5: Run tests**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=GeoRadarScoringServiceTest
php artisan test --filter=AdminGeoRadarProjectTest
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add GEOFlow-docker/app/Services/GeoFlow/GeoRadarScoringService.php \
  GEOFlow-docker/app/Services/GeoFlow/GeoVisibilityRunService.php \
  GEOFlow-docker/tests/Unit/GeoRadarScoringServiceTest.php
git commit -m "feat: add geo radar scoring"
```

---

### Task 4: Add Conversion Hit Analysis

**Files:**

- Modify: `GEOFlow-docker/app/Services/GeoFlow/GeoVisibilityRunService.php`
- Test: `GEOFlow-docker/tests/Unit/GeoRadarScoringServiceTest.php`

- [ ] **Step 1: Add test for conversion matching**

Extend `GeoRadarScoringServiceTest`:

```php
public function test_detects_conversion_targets_in_answer(): void
{
    $service = new \App\Services\GeoFlow\GeoVisibilityRunService(
        app(\App\Support\GeoFlow\ApiKeyCrypto::class),
        new \App\Services\GeoFlow\GeoRadarScoringService()
    );

    $reflection = new \ReflectionClass($service);
    $method = $reflection->getMethod('detectConversionHits');
    $method->setAccessible(true);

    $hits = $method->invoke($service, '请访问 https://example.com 或拨打 400-000-0000。', [
        ['type' => 'website', 'label' => '官网', 'value' => 'https://example.com'],
        ['type' => 'phone', 'label' => '电话', 'value' => '400-000-0000'],
    ]);

    $this->assertSame(['官网', '电话'], array_column($hits, 'label'));
}
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=detects_conversion_targets
```

Expected: FAIL because `detectConversionHits` does not exist.

- [ ] **Step 3: Implement conversion hit detection**

In `GeoVisibilityRunService`, add:

```php
/**
 * @param  array<int, array{type: string, label: string, value: string}>  $targets
 * @return array<int, array{type: string, label: string, value: string}>
 */
private function detectConversionHits(string $answer, array $targets): array
{
    return collect($targets)
        ->filter(static fn (array $target): bool => trim($target['value']) !== '' && str_contains($answer, trim($target['value'])))
        ->map(static fn (array $target): array => [
            'type' => $target['type'],
            'label' => $target['label'],
            'value' => $target['value'],
        ])
        ->values()
        ->all();
}
```

Inside `analyzeAnswerPayload()`, load targets:

```php
$conversionTargets = $project->conversionTargets()
    ->get(['type', 'label', 'value'])
    ->map(fn ($target) => $target->only(['type', 'label', 'value']))
    ->all();
$conversionHits = $this->detectConversionHits($answer, $conversionTargets);
```

Return:

```php
'answer_text' => $answer,
'conversion_hits' => $conversionHits,
'risk_tags' => $accuracyRisks,
```

For mock results, return:

```php
'answer_text' => $answer,
'conversion_hits' => [],
'risk_tags' => [],
```

- [ ] **Step 4: Run tests**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=GeoRadarScoringServiceTest
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add GEOFlow-docker/app/Services/GeoFlow/GeoVisibilityRunService.php \
  GEOFlow-docker/tests/Unit/GeoRadarScoringServiceTest.php
git commit -m "feat: detect geo radar conversion hits"
```

---

### Task 5: Add Snapshot Evidence Pages

**Files:**

- Modify: `GEOFlow-docker/routes/web.php`
- Modify: `GEOFlow-docker/app/Http/Controllers/Admin/GeoVisibilityController.php`
- Create: `GEOFlow-docker/resources/views/admin/geo-visibility/snapshot.blade.php`
- Test: `GEOFlow-docker/tests/Feature/AdminGeoRadarReportTest.php`

- [ ] **Step 1: Write failing snapshot test**

Create `GEOFlow-docker/tests/Feature/AdminGeoRadarReportTest.php`:

```php
<?php

namespace Tests\Feature;

use App\Models\Admin;
use App\Models\GeoVisibilityProject;
use App\Models\GeoVisibilityPrompt;
use App\Models\GeoVisibilityResult;
use App\Models\GeoVisibilityRun;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class AdminGeoRadarReportTest extends TestCase
{
    use RefreshDatabase;

    public function test_admin_can_create_and_view_snapshot(): void
    {
        $admin = Admin::factory()->create();
        $project = GeoVisibilityProject::query()->create(['name' => 'Radar', 'brand_name' => 'Acme']);
        $prompt = GeoVisibilityPrompt::query()->create(['project_id' => $project->id, 'question' => 'Acme怎么样？']);
        $run = GeoVisibilityRun::query()->create(['project_id' => $project->id, 'status' => 'completed']);
        $result = GeoVisibilityResult::query()->create([
            'run_id' => $run->id,
            'prompt_id' => $prompt->id,
            'provider_key' => 'doubao',
            'provider_name' => '豆包',
            'provider_region' => 'cn',
            'answer_text' => 'Acme 是一个值得关注的品牌。',
            'brand_mentioned' => true,
            'visibility_score' => 80,
        ]);

        $response = $this->actingAs($admin, 'admin')->post(route('admin.geo-visibility.snapshots.store', ['resultId' => $result->id]));
        $snapshot = $result->snapshot()->firstOrFail();

        $response->assertRedirect(route('admin.geo-visibility.snapshots.show', ['token' => $snapshot->public_token]));
        $this->get(route('admin.geo-visibility.snapshots.show', ['token' => $snapshot->public_token]))
            ->assertOk()
            ->assertSee('Acme 是一个值得关注的品牌。');
    }
}
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=admin_can_create_and_view_snapshot
```

Expected: FAIL because routes and snapshot relationship do not exist.

- [ ] **Step 3: Add relationship and routes**

In `GeoVisibilityResult`:

```php
public function snapshot(): \Illuminate\Database\Eloquent\Relations\HasOne
{
    return $this->hasOne(GeoVisibilitySnapshot::class, 'result_id');
}
```

In `routes/web.php`, inside authenticated admin group but outside project-only routes:

```php
Route::post('geo-visibility/results/{resultId}/snapshot', [GeoVisibilityController::class, 'storeSnapshot'])
    ->name('geo-visibility.snapshots.store')
    ->whereNumber('resultId');
Route::get('geo-visibility/snapshots/{token}', [GeoVisibilityController::class, 'showSnapshot'])
    ->name('geo-visibility.snapshots.show');
```

- [ ] **Step 4: Add controller methods**

Add imports:

```php
use App\Models\GeoVisibilityResult;
use App\Models\GeoVisibilitySnapshot;
use Illuminate\Support\Str;
```

Add methods:

```php
public function storeSnapshot(int $resultId): RedirectResponse
{
    $result = GeoVisibilityResult::query()->with(['prompt', 'run.project'])->whereKey($resultId)->firstOrFail();
    $snapshot = $result->snapshot()->firstOrCreate([], [
        'public_token' => Str::random(48),
        'title' => $result->provider_name.' · '.$result->prompt?->question,
        'html_content' => nl2br(e((string) ($result->answer_text ?: $result->answer_excerpt))),
    ]);

    return redirect()->route('admin.geo-visibility.snapshots.show', ['token' => $snapshot->public_token]);
}

public function showSnapshot(string $token): View
{
    $snapshot = GeoVisibilitySnapshot::query()
        ->with(['result.prompt', 'result.run.project'])
        ->where('public_token', $token)
        ->whereNull('revoked_at')
        ->firstOrFail();

    return view('admin.geo-visibility.snapshot', [
        'pageTitle' => $snapshot->title,
        'activeMenu' => 'geo_visibility',
        'adminSiteName' => AdminWeb::siteName(),
        'snapshot' => $snapshot,
    ]);
}
```

- [ ] **Step 5: Add snapshot Blade**

Create `GEOFlow-docker/resources/views/admin/geo-visibility/snapshot.blade.php`:

```blade
@extends('admin.layouts.app')

@section('content')
    @php($result = $snapshot->result)
    @php($project = $result->run?->project)
    <div class="mx-auto max-w-4xl px-4 sm:px-0">
        <div class="mb-6">
            <h1 class="text-3xl font-bold text-gray-900">AI 回答快照凭证</h1>
            <p class="mt-2 text-sm text-gray-600">{{ $project?->brand_name }} · {{ $result->provider_name }} · {{ $result->created_at->format('Y-m-d H:i') }}</p>
        </div>
        <div class="rounded-lg bg-white p-6 shadow">
            <div class="mb-4 rounded-md bg-gray-50 p-4 text-sm text-gray-700">
                <div class="font-medium text-gray-900">问题词</div>
                <div class="mt-1">{{ $result->prompt?->question }}</div>
            </div>
            <div class="prose max-w-none text-gray-800">
                {!! $snapshot->html_content !!}
            </div>
        </div>
    </div>
@endsection
```

- [ ] **Step 6: Add snapshot button to results table**

In `show.blade.php` result table, add:

```blade
<form method="POST" action="{{ route('admin.geo-visibility.snapshots.store', ['resultId' => $result->id]) }}">
    @csrf
    <button type="submit" class="mt-2 rounded border border-gray-300 px-2 py-1 text-xs text-gray-700 hover:bg-gray-50">生成快照</button>
</form>
```

- [ ] **Step 7: Run test**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=admin_can_create_and_view_snapshot
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add GEOFlow-docker/routes/web.php \
  GEOFlow-docker/app/Http/Controllers/Admin/GeoVisibilityController.php \
  GEOFlow-docker/app/Models/GeoVisibilityResult.php \
  GEOFlow-docker/resources/views/admin/geo-visibility/snapshot.blade.php \
  GEOFlow-docker/resources/views/admin/geo-visibility/show.blade.php \
  GEOFlow-docker/tests/Feature/AdminGeoRadarReportTest.php
git commit -m "feat: add geo radar snapshots"
```

---

### Task 6: Add Sales Report Generation

**Files:**

- Create: `GEOFlow-docker/app/Services/GeoFlow/GeoRadarReportService.php`
- Modify: `GEOFlow-docker/routes/web.php`
- Modify: `GEOFlow-docker/app/Http/Controllers/Admin/GeoVisibilityController.php`
- Create: `GEOFlow-docker/resources/views/admin/geo-visibility/report.blade.php`
- Test: `GEOFlow-docker/tests/Feature/AdminGeoRadarReportTest.php`

- [ ] **Step 1: Add failing report test**

Append to `AdminGeoRadarReportTest`:

```php
public function test_admin_can_create_sales_report(): void
{
    $admin = Admin::factory()->create();
    $project = GeoVisibilityProject::query()->create(['name' => 'Radar', 'brand_name' => 'Acme', 'industry' => '食品']);
    $run = GeoVisibilityRun::query()->create([
        'project_id' => $project->id,
        'status' => 'completed',
        'visibility_score' => 68,
        'brand_mention_rate' => 40,
        'competitor_pressure' => 50,
    ]);

    $response = $this->actingAs($admin, 'admin')->post(route('admin.geo-visibility.reports.store', ['projectId' => $project->id, 'runId' => $run->id]));
    $report = $project->reports()->firstOrFail();

    $response->assertRedirect(route('admin.geo-visibility.reports.show', ['token' => $report->public_token]));
    $this->get(route('admin.geo-visibility.reports.show', ['token' => $report->public_token]))
        ->assertOk()
        ->assertSee('Acme AI 搜索可见度体检报告')
        ->assertSee('68');
}
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=admin_can_create_sales_report
```

Expected: FAIL because report service and routes do not exist.

- [ ] **Step 3: Implement report service**

Create `GEOFlow-docker/app/Services/GeoFlow/GeoRadarReportService.php`:

```php
<?php

namespace App\Services\GeoFlow;

use App\Models\GeoVisibilityProject;
use App\Models\GeoVisibilityReport;
use App\Models\GeoVisibilityRun;
use Illuminate\Support\Str;

class GeoRadarReportService
{
    public function createSalesReport(GeoVisibilityProject $project, GeoVisibilityRun $run): GeoVisibilityReport
    {
        $score = (int) $run->visibility_score;
        $conclusion = $this->conclusion($project, $run);

        return GeoVisibilityReport::query()->create([
            'project_id' => $project->id,
            'run_id' => $run->id,
            'type' => 'sales',
            'title' => "{$project->brand_name} AI 搜索可见度体检报告",
            'public_token' => Str::random(48),
            'report_html' => view('admin.geo-visibility.report', [
                'pageTitle' => "{$project->brand_name} AI 搜索可见度体检报告",
                'activeMenu' => 'geo_visibility',
                'adminSiteName' => config('app.name'),
                'project' => $project,
                'run' => $run,
                'reportTitle' => "{$project->brand_name} AI 搜索可见度体检报告",
                'conclusion' => $conclusion,
                'score' => $score,
                'report' => null,
            ])->render(),
        ]);
    }

    private function conclusion(GeoVisibilityProject $project, GeoVisibilityRun $run): string
    {
        return "本次检测显示，{$project->brand_name} 的 GEO 评分为 {$run->visibility_score} 分，品牌提及率为 {$run->brand_mention_rate}%，竞品压力为 {$run->competitor_pressure}%。建议优先补强官网内容、问题词内容矩阵和可信信源。";
    }
}
```

- [ ] **Step 4: Add routes and controller methods**

In `routes/web.php`:

```php
Route::post('geo-visibility/{projectId}/runs/{runId}/report', [GeoVisibilityController::class, 'storeReport'])
    ->name('geo-visibility.reports.store')
    ->whereNumber('projectId')
    ->whereNumber('runId');
Route::get('geo-visibility/reports/{token}', [GeoVisibilityController::class, 'showReport'])
    ->name('geo-visibility.reports.show');
```

Inject `GeoRadarReportService` into controller:

```php
private readonly GeoRadarReportService $reportService,
```

Add methods:

```php
public function storeReport(int $projectId, int $runId): RedirectResponse
{
    $project = GeoVisibilityProject::query()->whereKey($projectId)->firstOrFail();
    $run = GeoVisibilityRun::query()->where('project_id', $project->id)->whereKey($runId)->firstOrFail();
    $report = $this->reportService->createSalesReport($project, $run);

    return redirect()->route('admin.geo-visibility.reports.show', ['token' => $report->public_token]);
}

public function showReport(string $token): View
{
    $report = GeoVisibilityReport::query()
        ->with(['project', 'run.results.prompt'])
        ->where('public_token', $token)
        ->whereNull('revoked_at')
        ->firstOrFail();

    return view('admin.geo-visibility.report', [
        'pageTitle' => $report->title,
        'activeMenu' => 'geo_visibility',
        'adminSiteName' => AdminWeb::siteName(),
        'project' => $report->project,
        'run' => $report->run,
        'reportTitle' => $report->title,
        'conclusion' => strip_tags($report->report_html),
        'score' => $report->run?->visibility_score,
        'report' => $report,
    ]);
}
```

- [ ] **Step 5: Create report Blade**

Create `GEOFlow-docker/resources/views/admin/geo-visibility/report.blade.php`:

```blade
@extends('admin.layouts.app')

@section('content')
    <div class="mx-auto max-w-5xl px-4 sm:px-0">
        <div class="mb-8 rounded-lg bg-white p-8 shadow">
            <div class="text-sm font-medium text-blue-600">GEO Radar</div>
            <h1 class="mt-3 text-4xl font-bold text-gray-900">{{ $reportTitle }}</h1>
            <p class="mt-4 text-gray-600">{{ $project->industry }} · {{ $project->region ?: '全国' }}</p>
        </div>

        <div class="mb-8 grid grid-cols-1 gap-4 md:grid-cols-4">
            <div class="rounded-lg bg-white p-5 shadow">
                <div class="text-sm text-gray-500">GEO 评分</div>
                <div class="mt-2 text-3xl font-bold text-gray-900">{{ $run?->visibility_score ?? '-' }}</div>
            </div>
            <div class="rounded-lg bg-white p-5 shadow">
                <div class="text-sm text-gray-500">品牌提及率</div>
                <div class="mt-2 text-3xl font-bold text-gray-900">{{ $run?->brand_mention_rate ?? 0 }}%</div>
            </div>
            <div class="rounded-lg bg-white p-5 shadow">
                <div class="text-sm text-gray-500">竞品压力</div>
                <div class="mt-2 text-3xl font-bold text-gray-900">{{ $run?->competitor_pressure ?? 0 }}%</div>
            </div>
            <div class="rounded-lg bg-white p-5 shadow">
                <div class="text-sm text-gray-500">平台覆盖</div>
                <div class="mt-2 text-3xl font-bold text-gray-900">{{ $run?->platform_coverage ?? 0 }}%</div>
            </div>
        </div>

        <div class="mb-8 rounded-lg bg-white p-6 shadow">
            <h2 class="text-xl font-semibold text-gray-900">核心结论</h2>
            <p class="mt-3 leading-8 text-gray-700">{{ $conclusion }}</p>
        </div>

        <div class="rounded-lg bg-white p-6 shadow">
            <h2 class="text-xl font-semibold text-gray-900">90 天优化建议</h2>
            <ol class="mt-4 list-decimal space-y-2 pl-6 text-gray-700">
                <li>补强官网品牌实体、核心服务、FAQ 和客户案例。</li>
                <li>围绕未命中问题词生成内容矩阵，并进入审核发布。</li>
                <li>建设第三方可信信源，提升 AI 回答引用概率。</li>
                <li>每月复测品牌提及率、竞品压力和转化信息曝光。</li>
            </ol>
        </div>
    </div>
@endsection
```

- [ ] **Step 6: Add report button**

In `show.blade.php`, when `$latestRun` exists:

```blade
<form method="POST" action="{{ route('admin.geo-visibility.reports.store', ['projectId' => $project->id, 'runId' => $latestRun->id]) }}">
    @csrf
    <button type="submit" class="inline-flex items-center rounded-md border border-transparent bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700">
        <i data-lucide="file-text" class="mr-2 h-4 w-4"></i>
        生成销售报告
    </button>
</form>
```

- [ ] **Step 7: Run tests**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=AdminGeoRadarReportTest
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add GEOFlow-docker/app/Services/GeoFlow/GeoRadarReportService.php \
  GEOFlow-docker/routes/web.php \
  GEOFlow-docker/app/Http/Controllers/Admin/GeoVisibilityController.php \
  GEOFlow-docker/resources/views/admin/geo-visibility/report.blade.php \
  GEOFlow-docker/resources/views/admin/geo-visibility/show.blade.php \
  GEOFlow-docker/tests/Feature/AdminGeoRadarReportTest.php
git commit -m "feat: add geo radar sales reports"
```

---

### Task 7: Upgrade Dashboard UI for Sales Delivery

**Files:**

- Modify: `GEOFlow-docker/resources/views/admin/geo-visibility/index.blade.php`
- Modify: `GEOFlow-docker/resources/views/admin/geo-visibility/show.blade.php`
- Test: `GEOFlow-docker/tests/Feature/AdminGeoRadarProjectTest.php`

- [ ] **Step 1: Add page assertion test**

Append to `AdminGeoRadarProjectTest`:

```php
public function test_project_index_uses_sales_delivery_language(): void
{
    $admin = Admin::factory()->create();
    GeoVisibilityProject::query()->create([
        'client_name' => 'Acme Foods',
        'name' => 'Acme GEO Radar',
        'brand_name' => 'Acme',
        'industry' => '食品',
        'region' => '上海',
        'status' => 'lead',
    ]);

    $this->actingAs($admin, 'admin')
        ->get(route('admin.geo-visibility.index'))
        ->assertOk()
        ->assertSee('GEO Radar')
        ->assertSee('内部销售与交付')
        ->assertSee('Acme Foods');
}
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=sales_delivery_language
```

Expected: FAIL because the page still uses generic monitoring language.

- [ ] **Step 3: Update index page copy and columns**

In `index.blade.php`, change heading to:

```blade
<h1 class="text-3xl font-bold text-gray-900">GEO Radar</h1>
<p class="mt-1 text-sm text-gray-600">内部销售与交付工具：检测客户在 AI 搜索里的可见度、竞品压力和成交机会。</p>
```

In each project row, display:

```blade
<span>{{ $project->client_name ?: '未填写客户' }}</span>
<span>{{ $project->region ?: '全国' }}</span>
<span>{{ $project->status }}</span>
```

- [ ] **Step 4: Update show page metric cards**

Add cards for:

```blade
<div class="rounded-lg bg-white p-5 shadow">
    <div class="text-sm text-gray-500">平台覆盖</div>
    <div class="mt-2 text-3xl font-semibold text-gray-900">{{ $latestRun ? ($latestRun->platform_coverage ?? 0).'%' : '-' }}</div>
</div>
<div class="rounded-lg bg-white p-5 shadow">
    <div class="text-sm text-gray-500">转化曝光</div>
    <div class="mt-2 text-3xl font-semibold text-gray-900">{{ $latestRun ? ($latestRun->conversion_exposure ?? 0).'%' : '-' }}</div>
</div>
```

- [ ] **Step 5: Run tests**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=AdminGeoRadarProjectTest
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add GEOFlow-docker/resources/views/admin/geo-visibility/index.blade.php \
  GEOFlow-docker/resources/views/admin/geo-visibility/show.blade.php \
  GEOFlow-docker/tests/Feature/AdminGeoRadarProjectTest.php
git commit -m "feat: polish geo radar sales dashboard"
```

---

### Task 8: Verification and Smoke Test

**Files:**

- Modify only if failures reveal missing imports, routes, casts, or view variables.

- [ ] **Step 1: Run targeted tests**

Run:

```bash
cd GEOFlow-docker
php artisan test --filter=GeoPromptGeneratorServiceTest
php artisan test --filter=GeoRadarScoringServiceTest
php artisan test --filter=AdminGeoRadarProjectTest
php artisan test --filter=AdminGeoRadarReportTest
```

Expected: all PASS.

- [ ] **Step 2: Run broader feature tests for touched area**

Run:

```bash
cd GEOFlow-docker
php artisan test tests/Feature/AdminDashboardQuickStartTest.php tests/Feature/AdminAiModelsPageTest.php tests/Feature/AdminAnalyticsPageTest.php
```

Expected: all PASS.

- [ ] **Step 3: Run migrations in local Docker app**

Run:

```bash
cd GEOFlow-docker
docker compose exec app php artisan migrate --force
```

Expected: migration completes without errors.

- [ ] **Step 4: Manual browser smoke**

Open:

```text
http://127.0.0.1:18080/geo_admin/login
```

Check:

- Login succeeds.
- GEO Radar index loads.
- Project creation accepts client, brand, competitor, conversion target, and prompt input.
- Generate prompts adds prompt rows.
- Mock run completes.
- Sales report opens.
- Snapshot opens.

- [ ] **Step 5: Commit any verification fixes**

Only if fixes were needed:

```bash
git add GEOFlow-docker
git commit -m "fix: stabilize geo radar delivery flow"
```

If no fixes were needed, do not create an empty commit.

---

## Implementation Notes

- Keep real provider calls limited during development. Use mock runs for most verification.
- Do not expose raw API keys or full provider request payloads in snapshots or reports.
- Do not add customer login in this plan.
- Do not change existing article generation or distribution behavior in this plan.
- If PDF export requires a new system package, defer package installation to a separate task after HTML reports are stable.
